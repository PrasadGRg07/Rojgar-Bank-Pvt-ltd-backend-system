from django.contrib.auth import authenticate, get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from apps.employee.models import Subscription


from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


@method_decorator(csrf_exempt, name='dispatch')
class SuperAdminLoginView(APIView):

    authentication_classes = []
    permission_classes = []


    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(username=username, password=password)

        if user is None:
            return Response(
                {"message": "Invalid username or password"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if user.role != "superadmin":
            return Response(
                {"message": "You are not a Super Admin"},
                status=status.HTTP_403_FORBIDDEN,
            )

        refresh = RefreshToken.for_user(user)

        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "id": user.id,
                "username": user.username,
                "role": "superadmin",
            }
        })


class SuperAdminSubscriptionListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from django.utils import timezone
        subs = Subscription.objects.select_related('user', 'reviewed_by').all()
        data = []
        for s in subs:
            # Auto-expire check
            s.check_and_expire()
            slip_url = None
            if s.payment_slip:
                try:
                    slip_url = request.build_absolute_uri(s.payment_slip.url)
                except Exception:
                    pass
            days_remaining = None
            if s.expires_at and s.status == 'active':
                delta = s.expires_at - timezone.now()
                days_remaining = max(0, delta.days)
            data.append({
                'id': s.id,
                'employee': s.user.username,
                'email': s.user.email,
                'plan': s.plan,
                'amount': str(s.amount),
                'status': s.status,
                'status_display': s.get_status_display(),
                'payment_slip': slip_url,
                'admin_note': s.admin_note,
                'reviewed_by': s.reviewed_by.username if s.reviewed_by else None,
                'rejection_reason': s.rejection_reason,
                'expires_at': s.expires_at.strftime('%Y-%m-%d') if s.expires_at else None,
                'days_remaining': days_remaining,
                'activated_at': s.activated_at.strftime('%Y-%m-%d') if s.activated_at else None,
                'created_at': s.created_at.strftime('%Y-%m-%d'),
            })
        return Response(data)


class SuperAdminActivateSubscriptionView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        from django.utils import timezone
        from datetime import timedelta

        sub = get_object_or_404(Subscription, pk=pk)
        now = timezone.now()

        duration_days = Subscription.PLAN_DURATION_DAYS.get(sub.plan)
        expires_at = now + timedelta(days=duration_days) if duration_days else None

        sub.status = 'active'
        sub.activated_by = request.user
        sub.activated_at = now
        sub.expires_at = expires_at
        sub.save()

        expiry_str = expires_at.strftime('%Y-%m-%d') if expires_at else 'Never'
        return Response({
            'message': f'Subscription activated. {sub.user.username} now has {sub.plan} plan.',
            'status': sub.status,
            'expires_at': expiry_str,
        })


class SuperAdminRejectSubscriptionView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        sub = get_object_or_404(Subscription, pk=pk)
        reason = request.data.get('reason', 'Rejected by superadmin.')
        sub.status = 'rejected'
        sub.rejection_reason = reason
        sub.activated_by = request.user
        sub.save()
        return Response({
            'message': 'Subscription rejected.',
            'status': sub.status,
        })


class SuperAdminUpdateSubscriptionView(APIView):
    """Allows superadmin to freely change status and/or expiry date of any subscription."""
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        from django.utils import timezone
        from datetime import datetime

        sub = get_object_or_404(Subscription, pk=pk)
        new_status = request.data.get('status')
        new_expires_at = request.data.get('expires_at')  # expected: 'YYYY-MM-DD'

        if new_status and new_status in dict(Subscription.STATUS_CHOICES):
            sub.status = new_status
            # If re-activating, set activated_at
            if new_status == 'active' and not sub.activated_at:
                sub.activated_at = timezone.now()

        if new_expires_at:
            try:
                sub.expires_at = datetime.strptime(new_expires_at, '%Y-%m-%d').replace(
                    tzinfo=timezone.now().tzinfo
                )
            except ValueError:
                return Response({'detail': 'Invalid date format. Use YYYY-MM-DD.'}, status=400)

        sub.save()
        return Response({
            'message': 'Subscription updated.',
            'status': sub.status,
            'expires_at': sub.expires_at.strftime('%Y-%m-%d') if sub.expires_at else None,
        })

class SuperAdminUserListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != "superadmin":
            return Response({"detail": "Forbidden"}, status=403)
        User = get_user_model()
        users = User.objects.all().order_by("-date_joined")
        data = []
        for user in users:
            data.append({
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role,
                "date_joined": user.date_joined.strftime("%Y-%m-%d"),
            })
        return Response(data)

class SuperAdminPromoteUserView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        if request.user.role != "superadmin":
            return Response({"detail": "Forbidden"}, status=403)
        User = get_user_model()
        user = get_object_or_404(User, pk=pk)
        
        user.role = "superadmin"
        user.save()
        
        return Response({
            "message": f"User {user.username} has been granted unlimited access (superadmin).",
            "role": user.role
        })