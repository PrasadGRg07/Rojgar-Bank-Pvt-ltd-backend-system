"""Backend enforcement of the Free Plan job-posting rule.

Mirrors the acceptance criteria for the subscription popup / job-post limit so
the rules are provably identical on the server, independent of the frontend.
"""

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from apps.employee.models import Job, Subscription
from apps.employee.plan_utils import (
    FREE_PLAN_JOB_LIMIT,
    get_effective_plan,
    get_job_posting_status,
    is_paid_user,
)

User = get_user_model()

JOB_PAYLOAD = {"title": "Software Engineer", "description": "Full stack role"}


class SubscriptionJobQuotaTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="employer",
            email="employer@example.com",
            password="Password123!",
            role="employee",
            is_verified=True,
        )
        self.authenticate()

    def authenticate(self, user=None):
        """Log in over HTTP so the test exercises the real token flow."""
        target = user or self.user
        self.client.credentials()
        response = self.client.post(
            "/api/auth/login/",
            {"username": target.username, "password": "Password123!"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {response.data['access']}"
        )

    def create_job(self, **extra):
        return self.client.post(
            "/api/employee/jobs/", {**JOB_PAYLOAD, **extra}, format="json"
        )

    def activate_subscription(self, plan="professional", expires_in_days=30):
        subscription = Subscription.objects.create(
            user=self.user, plan=plan, amount=Subscription.PLAN_AMOUNTS[plan]
        )
        subscription.status = "active"
        subscription.activated_at = timezone.now()
        subscription.expires_at = timezone.now() + timedelta(days=expires_in_days)
        subscription.save()
        return subscription

    # ------------------------------------------------------------------
    # Scenario: new free employee
    # ------------------------------------------------------------------

    def test_new_employee_is_free_and_can_post(self):
        """A brand new employer starts on Free with 1 job available."""
        response = self.client.get("/api/employee/job-posting-status/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["plan"], "free")
        self.assertFalse(response.data["is_paid"])
        self.assertEqual(response.data["posted_jobs"], 0)
        self.assertEqual(response.data["free_limit"], FREE_PLAN_JOB_LIMIT)
        self.assertEqual(response.data["jobs_remaining"], 1)
        self.assertTrue(response.data["can_post_job"])
        # No upgrade prompt is warranted yet.
        self.assertFalse(response.data["requires_subscription"])

    # ------------------------------------------------------------------
    # Scenario: first post succeeds, then the limit is hit
    # ------------------------------------------------------------------

    def test_first_publish_succeeds_and_activates_the_limit(self):
        response = self.create_job(status="pending")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], "pending")

        status_response = self.client.get("/api/employee/job-posting-status/")

        self.assertEqual(status_response.data["posted_jobs"], 1)
        self.assertEqual(status_response.data["jobs_remaining"], 0)
        self.assertTrue(status_response.data["requires_subscription"])
        self.assertFalse(status_response.data["can_post_job"])

    def test_second_publish_is_blocked_with_clear_message(self):
        self.create_job(status="pending")

        response = self.create_job(title="Second Job", status="pending")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["code"], "subscription_required")
        self.assertTrue(response.data["requires_subscription"])
        self.assertIn("Upgrade to a subscription plan", response.data["message"])
        # The blocked job must not have been persisted.
        self.assertEqual(Job.objects.filter(user=self.user).count(), 1)

    def test_blocked_publish_returns_no_duplicate_notification_noise(self):
        self.create_job(status="pending")
        before = Job.objects.count()

        self.create_job(title="Blocked", status="pending")

        self.assertEqual(Job.objects.count(), before)

    # ------------------------------------------------------------------
    # Drafts must not consume the single free slot
    # ------------------------------------------------------------------

    def test_drafts_do_not_consume_quota(self):
        for index in range(3):
            response = self.create_job(title=f"Draft {index}", status="draft")
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        status_response = self.client.get("/api/employee/job-posting-status/")

        self.assertEqual(status_response.data["posted_jobs"], 0)
        self.assertTrue(status_response.data["can_post_job"])

        # And the real publish still goes through.
        self.assertEqual(
            self.create_job(title="Real Post", status="pending").status_code,
            status.HTTP_201_CREATED,
        )

    def test_draft_defaults_to_draft_when_status_omitted(self):
        response = self.create_job()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], "draft")

    # ------------------------------------------------------------------
    # submit-for-review is a second, independent gate
    # ------------------------------------------------------------------

    def test_submit_for_review_blocked_once_limit_reached(self):
        first = self.create_job(status="pending")
        second = self.create_job(title="Staged", status="draft")

        response = self.client.patch(
            f"/api/employee/jobs/{second.data['id']}/submit/"
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["code"], "subscription_required")

        second_job = Job.objects.get(pk=second.data["id"])
        self.assertEqual(second_job.status, "draft")

    def test_submit_for_review_allowed_for_first_job(self):
        draft = self.create_job(status="draft")

        response = self.client.patch(
            f"/api/employee/jobs/{draft.data['id']}/submit/"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Job.objects.get(pk=draft.data["id"]).status, "pending")

    # ------------------------------------------------------------------
    # Client cannot forge review-controlled status
    # ------------------------------------------------------------------

    def test_client_cannot_self_approve_a_job(self):
        response = self.create_job(status="approved")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Job.objects.filter(user=self.user).count(), 0)

    # ------------------------------------------------------------------
    # Paid subscribers
    # ------------------------------------------------------------------

    def test_paid_subscription_allows_unlimited_posts(self):
        self.activate_subscription("professional")

        status_response = self.client.get("/api/employee/job-posting-status/")

        self.assertEqual(status_response.data["plan"], "professional")
        self.assertTrue(status_response.data["is_paid"])
        self.assertIsNone(status_response.data["free_limit"])
        self.assertIsNone(status_response.data["jobs_remaining"])
        self.assertTrue(status_response.data["can_post_job"])
        self.assertFalse(status_response.data["requires_subscription"])

        for index in range(4):
            response = self.create_job(title=f"Paid Job {index}", status="pending")
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_status_survives_a_new_session(self):
        """Refreshing / logging back in must not resurrect the free plan."""
        self.activate_subscription("basic")

        self.authenticate()  # fresh login == new browser session

        status_response = self.client.get("/api/employee/job-posting-status/")

        self.assertEqual(status_response.data["plan"], "basic")
        self.assertTrue(status_response.data["is_paid"])
        self.assertTrue(status_response.data["can_post_job"])

    def test_expiring_a_subscription_restores_the_free_limit(self):
        self.activate_subscription("basic", expires_in_days=30)

        Subscription.objects.filter(user=self.user).update(
            expires_at=timezone.now() - timedelta(days=1)
        )

        status_response = self.client.get("/api/employee/job-posting-status/")

        self.assertEqual(status_response.data["plan"], "free")
        self.assertFalse(status_response.data["is_paid"])

        self.assertEqual(
            Subscription.objects.get(user=self.user).status, "expired"
        )

    def test_pending_subscription_does_not_unlock_posting(self):
        Subscription.objects.create(
            user=self.user, plan="professional", amount=2499, status="pending"
        )

        self.assertEqual(get_effective_plan(self.user), "free")
        self.assertFalse(is_paid_user(self.user))

        self.create_job(status="pending")
        response = self.create_job(title="Blocked", status="pending")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_active_free_plan_subscription_is_not_a_paid_entitlement(self):
        Subscription.objects.create(
            user=self.user, plan="free", amount=0, status="active"
        )

        self.assertEqual(get_effective_plan(self.user), "free")
        self.assertFalse(is_paid_user(self.user))

    def test_special_accounts_are_unlimited(self):
        self.user.is_special_account = True
        self.user.save()

        self.assertEqual(get_effective_plan(self.user), "special")

        for index in range(3):
            self.assertEqual(
                self.create_job(title=f"Special {index}", status="pending").status_code,
                status.HTTP_201_CREATED,
            )

    # ------------------------------------------------------------------
    # Dashboard payload + full activation flow
    # ------------------------------------------------------------------

    def test_dashboard_exposes_job_posting_entitlement(self):
        self.create_job(status="pending")

        response = self.client.get("/api/employee/dashboard/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("job_posting", response.data)
        self.assertTrue(response.data["job_posting"]["requires_subscription"])
        # Existing dashboard keys must be untouched.
        for key in ("total_jobs", "active_jobs", "total_applicants", "recent_applications"):
            self.assertIn(key, response.data)

    def test_activation_flow_unlocks_posting_end_to_end(self):
        """pending -> forwarded -> active must lift the block immediately."""
        subscription = Subscription.objects.create(
            user=self.user, plan="professional", amount=2499, status="pending"
        )

        self.create_job(status="pending")
        self.assertEqual(
            self.create_job(title="Blocked", status="pending").status_code,
            status.HTTP_403_FORBIDDEN,
        )

        superadmin = User.objects.create_user(
            username="root",
            password="Password123!",
            role="superadmin",
            is_verified=True,
        )
        self.authenticate(superadmin)

        activation = self.client.patch(
            f"/api/superadmin/subscriptions/{subscription.id}/activate/"
        )
        self.assertEqual(activation.status_code, status.HTTP_200_OK)

        self.authenticate(self.user)

        self.assertTrue(get_job_posting_status(self.user)["can_post_job"])
        self.assertEqual(
            self.create_job(title="Unlocked", status="pending").status_code,
            status.HTTP_201_CREATED,
        )

    def test_subscription_amount_is_server_side(self):
        response = self.client.post(
            "/api/employee/subscriptions/",
            {"plan": "professional", "amount": "1"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            Subscription.objects.get(pk=response.data["id"]).amount, 2499
        )

    def test_unknown_plan_is_rejected(self):
        response = self.client.post(
            "/api/employee/subscriptions/", {"plan": "platinum"}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_free_plan_is_not_queued_for_review(self):
        """Free is the default entitlement, so it must never reach the admin queue."""
        response = self.client.post(
            "/api/employee/subscriptions/", {"plan": "free"}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(
            Subscription.objects.filter(user=self.user, plan="free").exists()
        )

    def test_free_plan_submission_still_grants_default_entitlement(self):
        """A rejected free submission must not affect what the employer can do."""
        self.client.post(
            "/api/employee/subscriptions/", {"plan": "free"}, format="json"
        )

        status = get_job_posting_status(self.user)

        self.assertEqual(status["plan"], "free")
        self.assertFalse(status["is_paid"])
        self.assertTrue(status["can_post_job"])

    def test_job_posting_status_requires_authentication(self):
        self.client.credentials()

        self.assertEqual(
            self.client.get("/api/employee/job-posting-status/").status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_quota_is_per_employer(self):
        self.create_job(status="pending")

        other = User.objects.create_user(
            username="other",
            password="Password123!",
            role="employee",
            is_verified=True,
        )

        self.assertEqual(Job.objects.filter(user=other).count(), 0)
        self.assertTrue(get_job_posting_status(other)["can_post_job"])
