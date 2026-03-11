"""Views for the images app."""
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from rest_framework import generics
from rest_framework import permissions
from django_filters.rest_framework import DjangoFilterBackend

from .models import Image
from .serializers import ImageSerializer


@method_decorator(cache_page(300), name="dispatch")
@method_decorator(vary_on_headers("Authorization"), name="dispatch")
class ImageList(generics.ListCreateAPIView):
    """
    GET: List all images
    POST: Upload a new image
    """
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["motion_event"]


class ImageDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Retrieve a specific image
    PUT: Update image metadata
    DELETE: Delete an image
    """
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    permission_classes = [permissions.IsAuthenticated]
