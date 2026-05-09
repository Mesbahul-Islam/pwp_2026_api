"""URL routes for camera API endpoints."""

from django.urls import path
from . import views

urlpatterns = [
    path('', views.CameraList.as_view(), name='camera-list'),
    path('<uuid:uuid>/', views.CameraDetail.as_view(), name='camera-detail'),
    path('<uuid:uuid>/motions/', views.CameraMotionsList.as_view(), name='camera-motions'),
    path('<uuid:uuid>/images/', views.CameraImagesList.as_view(), name='camera-images'),
]
