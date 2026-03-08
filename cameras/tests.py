"""
Tests for camera model and related API endpoints.
"""

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Camera
from .serializers import CameraSerializer


class CameraModelTest(TestCase):
    """
    Test case for the Camera model.
    """
    def setUp(self):
        self.camera = Camera.objects.create(
            address="http://192.168.1.100:8080/video",
            resolution="1920x1080",
            fps=30,
            status="active"
        )

    def test_camera_creation(self):
        """
        Test camera creation.
        """
        self.assertEqual(self.camera.address, "http://192.168.1.100:8080/video")
        self.assertEqual(self.camera.resolution, "1920x1080")
        self.assertEqual(self.camera.fps, 30)
        self.assertEqual(self.camera.status, "active")

    def test_camera_str_representation(self):
        """
        Test camera string.
        """
        self.assertEqual(str(self.camera), "http://192.168.1.100:8080/video")

    def test_camera_default_values(self):
        """Test default values"""
        camera = Camera.objects.create(
            address="http://192.168.1.101:8080/video",
            resolution="1280x720"
        )
        self.assertEqual(camera.fps, 25)
        self.assertEqual(camera.status, "active")

    def test_camera_unique_address(self):
        with self.assertRaises(Exception):
            Camera.objects.create(
                address="http://192.168.1.100:8080/video",
                resolution="1280x720"
            )

    def test_camera_resolution_choices(self):
        self.assertIn(self.camera.resolution, [
            Camera.RESOLUTION_720P,
            Camera.RESOLUTION_1080P,
            Camera.RESOLUTION_4K
        ])


class CameraSerializerTest(TestCase):
    """
    Test for camera serializer
    """
    def setUp(self):
        self.camera_data = {
            "address": "http://192.168.1.102:8080/video",
            "resolution": "1920x1080",
            "fps": 30,
            "status": "active"
        }
        self.camera = Camera.objects.create(**self.camera_data)

    def test_serializer_contains_expected_fields(self):
        serializer = CameraSerializer(instance=self.camera)
        self.assertEqual(
            set(serializer.data.keys()),
            {'id', 'address', 'resolution', 'fps','status'}
        )

    def test_serializer_valid_data(self):
        data = {
            "address": "http://192.168.1.103:8080/video",
            "resolution": "1280x720",
            "fps": 25,
            "status": "active"
        }
        serializer = CameraSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_serializer_invalid_address(self):
        data = {
            "address": "not-a-valid-url",
            "resolution": "1280x720"
        }
        serializer = CameraSerializer(data=data)
        self.assertFalse(serializer.is_valid())


class CameraAPITest(APITestCase):
    """
    Test for camera API endpoints"""

    def setUp(self):
        self.camera = Camera.objects.create(
            address="http://192.168.1.100:8080/video",
            resolution="1920x1080",
            fps=30,
            status="active"
        )
        self.list_url = reverse('camera-list')
        self.detail_url = reverse('camera-detail', kwargs={'pk': self.camera.pk})

    def test_get_camera_list(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), Camera.objects.count())

    def test_get_camera_detail(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['address'], self.camera.address)

    def test_create_camera(self):
        data = {
            "address": "http://192.168.1.101:8080/video",
            "resolution": "1280x720",
            "fps": 25,
            "status": "active"
        }
        total_cameras = Camera.objects.count()
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Camera.objects.count(), total_cameras + 1)

    def test_update_camera(self):
        data = {
            "address": "http://192.168.1.100:8080/video",
            "resolution": "3840x2160",
            "fps": 60,
            "status": "inactive"
        }
        response = self.client.put(self.detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.camera.refresh_from_db()
        self.assertEqual(self.camera.resolution, "3840x2160")

    def test_partial_update_camera(self):
        data = {"status": "inactive"}
        response = self.client.patch(self.detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.camera.refresh_from_db()
        self.assertEqual(self.camera.status, "inactive")

    def test_delete_camera(self):
        total_cameras = Camera.objects.count()
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Camera.objects.count(), total_cameras - 1)

    def test_get_nonexistent_camera(self):
        url = reverse('camera-detail', kwargs={'pk': 9999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_camera_invalid_data(self):
        data = {
            "address": "not-a-url",
            "resolution": "invalid"
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_camera_motions_empty(self):
        url = reverse('camera-motions', kwargs={'pk': self.camera.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_get_camera_images_empty(self):
        url = reverse('camera-images', kwargs={'pk': self.camera.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
