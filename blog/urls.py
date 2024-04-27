from django.urls import path
from blog.views import (
    BlogPostCreateView,
    BlogPostDetailView,
    BlogPostUpdateView,
    BlogPostDeleteView,
    NumLetterClient,
    GetRandomPost
)
from blog.apps import BlogConfig

app_name = BlogConfig.name

urlpatterns = [
    path('create/', BlogPostCreateView.as_view(), name='create'),
    path("list/", GetRandomPost.as_view(), name="list"),
    path("view/<int:pk>/", BlogPostDetailView.as_view(), name="view"),
    path("edit/<int:pk>/", BlogPostUpdateView.as_view(), name="edit"),
    path("delete/<int:pk>", BlogPostDeleteView.as_view(), name="delete"),
    path("count/", NumLetterClient.as_view(), name="count"),
]
