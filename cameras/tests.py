"""
Tests for the cameras app.
Tests cover models, serializers, and API endpoints.
"""
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Camera
from .serializers import CameraSerializer


class CameraModelTest(TestCase):
    """Test cases for the Camera model."""

    def setUp(self):
        """Set up test data."""
        self.camera = Camera.objects.create(
            address="http://192.168.1.100:8080/video",
            resolution="1920x1080",
            fps=30,
            motion_sensitivity=0.25,
            status="active"
        )

    def test_camera_creation(self):
        """Test that a camera can be created."""
        self.assertEqual(self.camera.address, "http://192.168.1.100:8080/video")
        self.assertEqual(self.camera.resolution, "1920x1080")
        self.assertEqual(self.camera.fps, 30)
        self.assertEqual(self.camera.motion_sensitivity, 0.25)
        self.assertEqual(self.camera.status, "active")

    def test_camera_str_representation(self):
        """Test the string representation of a camera."""
        self.assertEqual(str(self.camera), "http://192.168.1.100:8080/video")

    def test_camera_default_values(self):
        """Test default values for camera fields."""
        camera = Camera.objects.create(
            address="http://192.168.1.101:8080/video",
            resolution="1280x720"
        )
        self.assertEqual(camera.fps, 25)
        self.assertEqual(camera.motion_sensitivity, 0.25)
        self.assertEqual(camera.status, "active")

    def test_camera_unique_address(self):
        """Test that camera address must be unique."""
        with self.assertRaises(Exception):
            Camera.objects.create(
                address="http://192.168.1.100:8080/video",
                resolution="1280x720"
            )

    def test_camera_resolution_choices(self):
        """Test valid resolution choices."""
        self.assertIn(self.camera.resolution, [
            Camera.RESOLUTION_720P,
            Camera.RESOLUTION_1080P,
            Camera.RESOLUTION_4K
        ])


class CameraSerializerTest(TestCase):
    """Test cases for the Camera serializer."""

    def setUp(self):
        """Set up test data."""
        self.camera_data = {
            "address": "http://192.168.1.102:8080/video",
            "resolution": "1920x1080",
            "fps": 30,
            "motion_sensitivity": 0.3,
            "status": "active"
        }
        self.camera = Camera.objects.create(**self.camera_data)

    def test_serializer_contains_expected_fields(self):
        """Test that serializer contains all expected fields."""
        serializer = CameraSerializer(instance=self.camera)
        self.assertEqual(
            set(serializer.data.keys()),
            {'id', 'address', 'resolution', 'fps', 'motion_sensitivity', 'status'}
        )

    def test_serializer_valid_data(self):
        """Test serializer with valid data."""
        data = {
            "address": "http://192.168.1.103:8080/video",
            "resolution": "1280x720",
            "fps": 25,
            "motion_sensitivity": 0.25,
            "status": "active"
        }
        serializer = CameraSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_serializer_invalid_address(self):
        """Test serializer with invalid address."""
        data = {
            "address": "not-a-valid-url",
            "resolution": "1280x720"
        }
        serializer = CameraSerializer(data=data)
        self.assertFalse(serializer.is_valid())


class CameraAPITest(APITestCase):
    """Test cases for the Camera API endpoints."""

    def setUp(self):
        """Set up test data."""
        self.camera = Camera.objects.create(
            address="http://192.168.1.100:8080/video",
            resolution="1920x1080",
            fps=30,
            motion_sensitivity=0.25,
            status="active"
        )
        self.list_url = reverse('camera-list')
        self.detail_url = reverse('camera-detail', kwargs={'pk': self.camera.pk})

    def test_get_camera_list(self):
        """Test GET request to list all cameras."""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_camera_detail(self):
        """Test GET request to retrieve a specific camera."""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['address'], self.camera.address)

    def test_create_camera(self):
        """Test POST request to create a new camera."""
        data = {
            "address": "http://192.168.1.101:8080/video",
            "resolution": "1280x720",
            "fps": 25,
            "motion_sensitivity": 0.3,
            "status": "active"
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Camera.objects.count(), 2)

    def test_update_camera(self):
        """Test PUT request to update a camera."""
        data = {
            "address": "http://192.168.1.100:8080/video",
            "resolution": "3840x2160",
            "fps": 60,
            "motion_sensitivity": 0.5,
            "status": "inactive"
        }
        response = self.client.put(self.detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.camera.refresh_from_db()
        self.assertEqual(self.camera.resolution, "3840x2160")

    def test_partial_update_camera(self):
        """Test PATCH request to partially update a camera."""
        data = {"status": "inactive"}
        response = self.client.patch(self.detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.camera.refresh_from_db()
        self.assertEqual(self.camera.status, "inactive")

    def test_delete_camera(self):
        """Test DELETE request to remove a camera."""
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Camera.objects.count(), 0)

    def test_get_nonexistent_camera(self):
        """Test GET request for a camera that doesn't exist."""
        url = reverse('camera-detail', kwargs={'pk': 9999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_camera_invalid_data(self):
        """Test POST request with invalid data."""
        data = {
            "address": "not-a-url",
            "resolution": "invalid"
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_camera_motions_empty(self):
        """Test GET request for camera motions when none exist."""
        url = reverse('camera-motions', kwargs={'pk': self.camera.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_get_camera_images_empty(self):
        """Test GET request for camera images when none exist."""
        url = reverse('camera-images', kwargs={'pk': self.camera.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
