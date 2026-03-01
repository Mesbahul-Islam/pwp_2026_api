from django.urls import path
from . import views

urlpatterns = [
    path('', views.MotionEventList.as_view(), name='motion-list'),
    path('<int:pk>/', views.MotionEventDetail.as_view(), name='motion-detail'),
    path('<int:pk>/images/', views.MotionEventImagesList.as_view(), name='motion-images'),
]
