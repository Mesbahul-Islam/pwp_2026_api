from django.urls import path
from . import views

urlpatterns = [
    path('', views.CameraList.as_view(), name='camera-list'),
    path('<int:pk>/', views.CameraDetail.as_view(), name='camera-detail'),
    path('<int:pk>/motions/', views.CameraMotionsList.as_view(), name='camera-motions'),
    path('<int:pk>/images/', views.CameraImagesList.as_view(), name='camera-images'),
]
