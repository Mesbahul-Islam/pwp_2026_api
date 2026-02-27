from django.urls import path
from . import views

urlpatterns = [
    path('', views.ImageList.as_view(), name='image-list'),
    path('<int:pk>/', views.ImageDetail.as_view(), name='image-detail'),
]
