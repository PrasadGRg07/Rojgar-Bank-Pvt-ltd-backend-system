"""Single source of truth for subscription entitlement and job-posting quota.

Both the API views and the frontend derive their decisions from here, so the
Free Plan rule ("1 job post, then subscribe") is enforced in exactly one place.

Definitions
-----------
effective plan
    The plan an employer is *actually* entitled to right now: the newest
    active paid subscription, otherwise ``"free"``. Special accounts are
    treated as ``"special"`` with unlimited access.

posted job
    Any ``Job`` row the employer has published. Drafts are excluded because a
    draft is a private, unpublished work-in-progress and not a job post. A
    rejected job still counts: the post succeeded, so the slot was consumed.
"""

from .models import Job, Subscription

# Number of jobs a Free Plan employer may publish. One is a hard business rule.
FREE_PLAN_JOB_LIMIT = 1

# Plans that grant unlimited job posting once activated.
PAID_PLANS = ("basic", "professional", "enterprise")

# A draft is not a published job post, so it never consumes quota.
NON_POSTING_JOB_STATUSES = ("draft",)


def get_active_paid_subscription(user):
    """Return the employer's active paid subscription, or ``None``.

    Expired subscriptions are flipped to ``"expired"`` as a side effect so the
    stored state stays honest, mirroring ``Subscription.check_and_expire``.
    """
    if user is None or not getattr(user, "is_authenticated", False):
        return None

    subscriptions = (
        Subscription.objects.filter(user=user, status="active")
        .order_by("-activated_at", "-created_at")
    )

    for subscription in subscriptions:
        if subscription.plan not in PAID_PLANS:
            continue

        if subscription.check_and_expire():
            # Just expired, so it grants no entitlement.
            continue

        return subscription

    return None


def get_effective_plan(user):
    """Return ``"special"``, a paid plan name, or ``"free"``."""
    if user is None or not getattr(user, "is_authenticated", False):
        return "free"

    if getattr(user, "is_special_account", False):
        return "special"

    subscription = get_active_paid_subscription(user)

    return subscription.plan if subscription else "free"


def is_paid_user(user):
    """True when the employer may post unlimited jobs."""
    return get_effective_plan(user) in ("special",) + PAID_PLANS


def count_posted_jobs(user):
    """Number of jobs the employer has actually published (drafts excluded)."""
    if user is None or not getattr(user, "is_authenticated", False):
        return 0

    return Job.objects.filter(user=user).exclude(
        status__in=NON_POSTING_JOB_STATUSES
    ).count()


def get_job_posting_status(user):
    """Full entitlement payload consumed by the dashboard and the job form."""
    plan = get_effective_plan(user)
    unlimited = plan == "special" or plan in PAID_PLANS
    posted_jobs = 0 if unlimited else count_posted_jobs(user)

    limit = None if unlimited else FREE_PLAN_JOB_LIMIT
    remaining = None if unlimited else max(0, limit - posted_jobs)
    requires_subscription = not unlimited and remaining <= 0

    return {
        "plan": plan,
        "is_paid": unlimited,
        "posted_jobs": posted_jobs,
        "free_limit": limit,
        "jobs_remaining": remaining,
        "can_post_job": not requires_subscription,
        "requires_subscription": requires_subscription,
    }


def subscription_required_response(status_payload=None):
    """403 payload the frontend uses to open the upgrade popup."""
    payload = status_payload or get_job_posting_status(None)

    return {
        "detail": (
            "Your free job post has been used. Upgrade to a subscription plan "
            "to continue posting unlimited jobs."
        ),
        "code": "subscription_required",
        "message": (
            "Your free job post has been used. Upgrade to a subscription plan "
            "to continue posting unlimited jobs."
        ),
        "requires_subscription": True,
        "plan": payload["plan"],
        "posted_jobs": payload["posted_jobs"],
        "free_limit": payload["free_limit"],
        "jobs_remaining": payload["jobs_remaining"],
    }
