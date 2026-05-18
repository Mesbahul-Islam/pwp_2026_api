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
from rest_framework.authtoken.views import obtain_auth_token
from .docs_views import client, openapi_yaml, swagger_ui

urlpatterns = [
    path('', client, name='client'),
    path('admin/', admin.site.urls),
    path('api/token/', obtain_auth_token, name='api-token-auth'),
    path('api/schema/', openapi_yaml, name='openapi-yaml'),
    path('api/docs/', swagger_ui, name='swagger-ui'),
    path('api/cameras/', include('cameras.urls')),
    path('api/motions/', include('motions.urls')),
    path('api/images/', include('images.urls')),
    path("api-auth/", include("rest_framework.urls"))
]
