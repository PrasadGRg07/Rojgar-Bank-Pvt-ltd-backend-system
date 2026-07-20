from django.urls import path
from .views import BlogArticleListCreateView, BlogArticleDetailView

urlpatterns = [
    path("articles/", BlogArticleListCreateView.as_view(), name="blog-article-list-create"),
    path("articles/<int:pk>/", BlogArticleDetailView.as_view(), name="blog-article-detail-id"),
    path("articles/<slug:slug>/", BlogArticleDetailView.as_view(), name="blog-article-detail"),
]
