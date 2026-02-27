from rest_framework import generics
from .models import Image
from .serializers import ImageSerializer


class ImageList(generics.ListCreateAPIView):
    """
    GET: List all images
    POST: Upload a new image
    """
    queryset = Image.objects.all()
    serializer_class = ImageSerializer


class ImageDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Retrieve a specific image
    PUT: Update image metadata
    DELETE: Delete an image
    """
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
