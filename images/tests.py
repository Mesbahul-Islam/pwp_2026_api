"""
Tests for the images app.
Tests cover models, serializers, and API endpoints.
"""
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from cameras.models import Camera
from motions.models import MotionEvent
from .models import Image
from .serializers import ImageSerializer


class ImageModelTest(TestCase):
    """Test cases for the Image model."""

    def setUp(self):
        """Set up test data."""
        self.camera = Camera.objects.create(
            address="http://192.168.1.100:8080/video",
            resolution="1920x1080",
            fps=30,
            motion_sensitivity=0.25,
            status="active"
        )
        self.motion_event = MotionEvent.objects.create(
            camera=self.camera,
            duration=5.5,
            threshold=0.3
        )
        self.image = Image.objects.create(
            motion_event=self.motion_event,
            filepath="http://example.com/images/capture_001.jpg",
            filesize=102400
        )

    def test_image_creation(self):
        """Test that an image can be created."""
        self.assertEqual(self.image.motion_event, self.motion_event)
        self.assertEqual(
            self.image.filepath,
            "http://example.com/images/capture_001.jpg"
        )
        self.assertEqual(self.image.filesize, 102400)

    def test_image_camera_property(self):
        """Test that camera is accessible via motion_event."""
        self.assertEqual(self.image.camera, self.camera)

    def test_image_str_representation(self):
        """Test the string representation of an image."""
        self.assertIn(self.camera.address, str(self.image))

    def test_image_auto_created_at(self):
        """Test that created_at is auto-generated."""
        self.assertIsNotNone(self.image.created_at)

    def test_image_nullable_filesize(self):
        """Test that filesize can be null."""
        image = Image.objects.create(
            motion_event=self.motion_event,
            filepath="http://example.com/images/capture_002.jpg"
        )
        self.assertIsNone(image.filesize)

    def test_image_motion_event_cascade_delete(self):
        """Test that images are deleted when motion event is deleted."""
        motion_id = self.motion_event.id
        self.motion_event.delete()
        self.assertEqual(
            Image.objects.filter(motion_event_id=motion_id).count(),
            0
        )

    def test_image_camera_cascade_via_motion(self):
        """Test that images are deleted when camera is deleted."""
        self.camera.delete()
        self.assertEqual(Image.objects.count(), 0)


class ImageSerializerTest(TestCase):
    """Test cases for the Image serializer."""

    def setUp(self):
        """Set up test data."""
        self.camera = Camera.objects.create(
            address="http://192.168.1.100:8080/video",
            resolution="1920x1080"
        )
        self.motion_event = MotionEvent.objects.create(
            camera=self.camera,
            duration=5.5
        )
        self.image = Image.objects.create(
            motion_event=self.motion_event,
            filepath="http://example.com/images/capture_001.jpg",
            filesize=102400
        )

    def test_serializer_contains_expected_fields(self):
        """Test that serializer contains all expected fields."""
        serializer = ImageSerializer(instance=self.image)
        self.assertEqual(
            set(serializer.data.keys()),
            {'id', 'camera', 'motion_event', 'filepath', 'filesize', 'created_at'}
        )

    def test_serializer_camera_derived_from_motion(self):
        """Test that camera is derived from motion event."""
        serializer = ImageSerializer(instance=self.image)
        self.assertEqual(serializer.data['camera'], self.camera.id)

    def test_serializer_valid_data(self):
        """Test serializer with valid data."""
        data = {
            "motion_event": self.motion_event.id,
            "filepath": "http://example.com/images/capture_002.jpg",
            "filesize": 204800
        }
        serializer = ImageSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_serializer_invalid_filepath(self):
        """Test serializer with invalid filepath."""
        data = {
            "motion_event": self.motion_event.id,
            "filepath": "not-a-valid-url"
        }
        serializer = ImageSerializer(data=data)
        self.assertFalse(serializer.is_valid())


class ImageAPITest(APITestCase):
    """Test cases for the Image API endpoints."""

    def setUp(self):
        """Set up test data."""
        self.camera = Camera.objects.create(
            address="http://192.168.1.100:8080/video",
            resolution="1920x1080",
            fps=30,
            motion_sensitivity=0.25,
            status="active"
        )
        self.motion_event = MotionEvent.objects.create(
            camera=self.camera,
            duration=5.5,
            threshold=0.3
        )
        self.image = Image.objects.create(
            motion_event=self.motion_event,
            filepath="http://example.com/images/capture_001.jpg",
            filesize=102400
        )
        self.list_url = reverse('image-list')
        self.detail_url = reverse('image-detail', kwargs={'pk': self.image.pk})

    def test_get_image_list(self):
        """Test GET request to list all images."""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_image_detail(self):
        """Test GET request to retrieve a specific image."""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['filepath'], self.image.filepath)

    def test_get_image_includes_camera(self):
        """Test that image response includes camera ID."""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['camera'], self.camera.id)

    def test_create_image(self):
        """Test POST request to create a new image."""
        data = {
            "motion_event": self.motion_event.id,
            "filepath": "http://example.com/images/capture_002.jpg",
            "filesize": 204800
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Image.objects.count(), 2)

    def test_update_image(self):
        """Test PUT request to update an image."""
        data = {
            "motion_event": self.motion_event.id,
            "filepath": "http://example.com/images/updated.jpg",
            "filesize": 512000
        }
        response = self.client.put(self.detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.image.refresh_from_db()
        self.assertEqual(self.image.filesize, 512000)

    def test_partial_update_image(self):
        """Test PATCH request to partially update an image."""
        data = {"filesize": 1024000}
        response = self.client.patch(self.detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.image.refresh_from_db()
        self.assertEqual(self.image.filesize, 1024000)

    def test_delete_image(self):
        """Test DELETE request to remove an image."""
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Image.objects.count(), 0)

    def test_get_nonexistent_image(self):
        """Test GET request for an image that doesn't exist."""
        url = reverse('image-detail', kwargs={'pk': 9999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_image_invalid_motion_event(self):
        """Test POST request with invalid motion event ID."""
        data = {
            "motion_event": 9999,
            "filepath": "http://example.com/images/capture.jpg"
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_camera_images_via_nested_route(self):
        """Test GET request for images via camera nested route."""
        url = reverse('camera-images', kwargs={'pk': self.camera.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_motion_images_via_nested_route(self):
        """Test GET request for images via motion nested route."""
        url = reverse('motion-images', kwargs={'pk': self.motion_event.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
