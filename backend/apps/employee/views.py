from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import EmployeeProfile

class EmployeeDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != 'employee':
            return Response({'detail': 'Forbidden'}, status=403)

        profile = getattr(request.user, 'employee_profile', None)

        return Response({
            'message': f'Welcome {request.user.get_full_name() or request.user.username}',
            'role': request.user.role,
            'department': profile.department if profile else None,
            'designation': profile.designation if profile else None,
        })