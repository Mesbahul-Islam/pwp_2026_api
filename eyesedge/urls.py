"""
URL configuration for eyesedge project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

from cameras import views as camera_views
from motions import views as motion_views
from images import views as image_views

router = routers.DefaultRouter()
router.register(r'cameras', camera_views.CameraList, basename='camera')
router.register(r'motions', motion_views.MotionEventList, basename='motionevent')
router.register(r'images', image_views.ImageList, basename='image')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/cameras/', include('cameras.urls')),
    path('api/motions/', include('motions.urls')),
    path('api/images/', include('images.urls')),
]
