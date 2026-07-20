from rest_framework import generics, permissions, status


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import JobSeekerProfile, Skill, Education, Experience, Certification
from .serializers import( JobSeekerProfileSerializer, SkillSerializer, 
                         CertificationSerializer,
                         EducationSerializer, ExperienceSerializer,
                         PortfolioSerializer, ResumeSerializer, AccountSettingsSerializer )

from django.shortcuts import get_object_or_404

# JobSeekerProfile views
#==================================SKILLS======================================================
class SkillListCreateView(generics.ListCreateAPIView):
    serializer_class = SkillSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        profile = JobSeekerProfile.objects.get(user=self.request.user)
        return Skill.objects.filter(profile=profile)
    
    def perform_create(self, serializer):
        profile = JobSeekerProfile.objects.get(user=self.request.user)
        serializer.save(profile=profile)
    
class SkillDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = SkillSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        profile = JobSeekerProfile.objects.get(user=self.request.user)
        return Skill.objects.filter(profile=profile)
    
    
#=============================PROFILE=========================
class JobSeekerProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = JobSeekerProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        profile, created = JobSeekerProfile.objects.get_or_create(
            user=self.request.user
        )
        return profile
    
    
    
    
#=======================================EDUCATION====================================
class EducationListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile, _ = JobSeekerProfile.objects.get_or_create(user=request.user)
        educations = profile.educations.all()

        serializer = EducationSerializer(
            educations,
            many=True,
        )

        return Response(serializer.data)

    def post(self, request):
        profile, _ = JobSeekerProfile.objects.get_or_create(user=request.user)

        serializer = EducationSerializer(
            data=request.data,
        )

        if serializer.is_valid():
            serializer.save(profile=profile)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )
class EducationDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, request, pk):
        profile, _ = JobSeekerProfile.objects.get_or_create(user=request.user)
        return get_object_or_404(Education, pk=pk, profile=profile)

    def get(self, request, pk):
        education = self.get_object(request, pk)

        serializer = EducationSerializer(
            education,
        )

        return Response(serializer.data)

    def put(self, request, pk):
        education = self.get_object(request, pk)

        serializer = EducationSerializer(
            education,
            data=request.data,
        )

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    def patch(self, request, pk):
        education = self.get_object(request, pk)

        serializer = EducationSerializer(
            education,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, pk):
        education = self.get_object(request, pk)

        education.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )


#++++++++++++++++++++++EXPERIENCES++++++++++++++++++++++++++++++++++++
class ExperienceListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile, _ = JobSeekerProfile.objects.get_or_create(user=request.user)
        experiences = profile.experiences.all()

        serializer = ExperienceSerializer(
            experiences,
            many=True,
        )

        return Response(serializer.data)

    def post(self, request):
        profile, _ = JobSeekerProfile.objects.get_or_create(user=request.user)

        serializer = ExperienceSerializer(
            data=request.data,
        )

        if serializer.is_valid():
            serializer.save(profile=profile)

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )
class ExperienceDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, request, pk):
        profile, _ = JobSeekerProfile.objects.get_or_create(user=request.user)
        return get_object_or_404(Experience, pk=pk, profile=profile)

    def get(self, request, pk):
        experience = self.get_object(request, pk)

        serializer = ExperienceSerializer(
            experience,
        )

        return Response(serializer.data)

    def put(self, request, pk):
        experience = self.get_object(request, pk)

        serializer = ExperienceSerializer(
            experience,
            data=request.data,
        )

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    def patch(self, request, pk):
        experience = self.get_object(request, pk)

        serializer = ExperienceSerializer(
            experience,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, pk):
        experience = self.get_object(request, pk)

        experience.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )

#======================CERTIFICATION===========================================
class CertificationListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile, _ = JobSeekerProfile.objects.get_or_create(user=request.user)

        certifications = profile.certifications.all()

        serializer = CertificationSerializer(
            certifications,
            many=True,
        )

        return Response(serializer.data)

    def post(self, request):
        profile, _ = JobSeekerProfile.objects.get_or_create(user=request.user)

        serializer = CertificationSerializer(
            data=request.data,
        )

        if serializer.is_valid():
            serializer.save(profile=profile)

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )
class CertificationDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, request, pk):
        profile, _ = JobSeekerProfile.objects.get_or_create(user=request.user)
        return get_object_or_404(Certification, pk=pk, profile=profile)

    def get(self, request, pk):
        certification = self.get_object(request, pk)

        serializer = CertificationSerializer(certification)

        return Response(serializer.data)

    def put(self, request, pk):
        certification = self.get_object(request, pk)

        serializer = CertificationSerializer(
            certification,
            data=request.data,
        )

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    def patch(self, request, pk):
        certification = self.get_object(request, pk)

        serializer = CertificationSerializer(
            certification,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, pk):
        certification = self.get_object(request, pk)

        certification.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )
        
        #================PORTFOLIO============================================
class PortfolioListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile, _ = JobSeekerProfile.objects.get_or_create(user=request.user)

        portfolios = profile.portfolios.all()

        serializer = PortfolioSerializer(
            portfolios,
            many=True,
        )

        return Response(serializer.data)

    def post(self, request):
        profile, _ = JobSeekerProfile.objects.get_or_create(user=request.user)

        serializer = PortfolioSerializer(
            data=request.data,
        )

        if serializer.is_valid():
            serializer.save(profile=profile)

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )
class PortfolioDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, request, pk):
        profile, _ = JobSeekerProfile.objects.get_or_create(user=request.user)
        return get_object_or_404(Portfolio, pk=pk, profile=profile)

    def get(self, request, pk):
        portfolio = self.get_object(request, pk)

        serializer = PortfolioSerializer(portfolio)

        return Response(serializer.data)

    def put(self, request, pk):
        portfolio = self.get_object(request, pk)

        serializer = PortfolioSerializer(
            portfolio,
            data=request.data,
        )

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    def patch(self, request, pk):
        portfolio = self.get_object(request, pk)

        serializer = PortfolioSerializer(
            portfolio,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, pk):
        portfolio = self.get_object(request, pk)

        portfolio.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
    
 #==================RESUME========================   
class ResumeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile, _ = JobSeekerProfile.objects.get_or_create(user=request.user)

        serializer = ResumeSerializer(
            profile,
            context={"request": request},
        )

        return Response(serializer.data)
class ResumeUploadView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        profile, _ = JobSeekerProfile.objects.get_or_create(user=request.user)

        serializer = ResumeSerializer(
            profile,
            data=request.data,
            partial=True,
            context={"request": request},
        )

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )
class ResumeDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        profile, _ = JobSeekerProfile.objects.get_or_create(user=request.user)

        if profile.resume:
            profile.resume.delete(save=False)

        profile.resume = None
        profile.save()

        return Response(
            {"message": "Resume deleted successfully."},
            status=status.HTTP_200_OK,
        )
#===========Settings(Account)===================================
class AccountSettingsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            profile = JobSeekerProfile.objects.get(user=request.user)
        except JobSeekerProfile.DoesNotExist:
            return Response(
                {"error": "Job seeker profile not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = AccountSettingsSerializer(profile)
        return Response(serializer.data)

    def put(self, request):
        try:
            profile = JobSeekerProfile.objects.get(user=request.user)
        except JobSeekerProfile.DoesNotExist:
            return Response(
                {"error": "Job seeker profile not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = AccountSettingsSerializer(
            profile,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "Account settings updated successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )