"""URL routes for image API endpoints."""

from django.urls import path
from . import views

urlpatterns = [
    path('', views.ImageList.as_view(), name='image-list'),
    path('<uuid:uuid>/', views.ImageDetail.as_view(), name='image-detail'),
]
