"""Views for the images app."""
from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend

from .models import Image
from .serializers import ImageSerializer


class ImageList(generics.ListCreateAPIView):
    """
    GET: List all images
    POST: Upload a new image
    """
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
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
