from django.urls import path
from .firebase_views import test_firestore
from .views import( JobSeekerProfileView, SkillListCreateView, 
                   SkillDetailView, EducationListCreateView, 
                   EducationDetailView, ExperienceDetailView, ExperienceListCreateView,
                   CertificationDetailView, CertificationListCreateView, PortfolioListCreateView,
                   PortfolioDetailView, ResumeView, ResumeUploadView, ResumeDeleteView, AccountSettingsView )


urlpatterns = [
    path("profile/", JobSeekerProfileView.as_view(), name="jobseeker-profile"),
    path('skills/', SkillListCreateView.as_view(), name='skill-list-create'),
    path('skills/<int:pk>/', SkillDetailView.as_view(), name='skill-detail'),
    path('education/', EducationListCreateView.as_view(), name='education-list-create'),
    path('education/<int:pk>/', EducationDetailView.as_view(), name='education-detail'),
    path('experience/', ExperienceListCreateView.as_view(), name='experience-list-create'),
    path('experience/<int:pk>/', ExperienceDetailView.as_view(), name='experience-detail'),
    path('certifications/', CertificationListCreateView.as_view(), name='certification-list-create'),
    path('certifications/<int:pk>/', CertificationDetailView.as_view(), name='certification-detail'),
    path('portfolio/', PortfolioListCreateView.as_view(), name='portfolio-list-create'),
    path('portfolio/<int:pk>/', PortfolioDetailView.as_view(), name='portfolio-detail'),
    path('resumes/', ResumeView.as_view(), name='resume-list-create'),
    path('resumes/upload/', ResumeUploadView.as_view(), name='resume-upload'),
    path('resumes/delete/', ResumeDeleteView.as_view(), name='resume-delete'),
    path("firebase-test/", test_firestore, name="firebase-test"),
    path('account-settings/', AccountSettingsView.as_view(), name='account-settings')


    
]