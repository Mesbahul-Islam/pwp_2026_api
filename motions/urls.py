"""URL routes for motion event API endpoints."""

from django.urls import path
from . import views

urlpatterns = [
    path('', views.MotionEventList.as_view(), name='motion-list'),
    path('<uuid:uuid>/', views.MotionEventDetail.as_view(), name='motion-detail'),
    path('<uuid:uuid>/images/', views.MotionEventImagesList.as_view(), name='motion-images'),
]
