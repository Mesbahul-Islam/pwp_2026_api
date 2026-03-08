"""
Tests for image and API endpoints.
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
    """
    Test case for the Image model.
    """
    def setUp(self):
        self.camera = Camera.objects.create(
            address="http://192.168.1.100:8080/video",
            resolution="1920x1080",
            fps=30,
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
        self.assertEqual(self.image.motion_event, self.motion_event)
        self.assertEqual(
            self.image.filepath,
            "http://example.com/images/capture_001.jpg"
        )
        self.assertEqual(self.image.filesize, 102400)

    def test_image_camera_property(self):
        self.assertEqual(self.image.camera, self.camera)

    def test_image_str_representation(self):
        self.assertIn(self.camera.address, str(self.image))

    def test_image_auto_created_at(self):
        self.assertIsNotNone(self.image.created_at)

    def test_image_nullable_filesize(self):
        image = Image.objects.create(
            motion_event=self.motion_event,
            filepath="http://example.com/images/capture_002.jpg"
        )
        self.assertIsNone(image.filesize)

    def test_image_motion_event_cascade_delete(self):
        motion_id = self.motion_event.id
        self.motion_event.delete()
        self.assertEqual(
            Image.objects.filter(motion_event_id=motion_id).count(),
            0
        )

    def test_image_camera_cascade_via_motion(self):
        count_before = Image.objects.count()
        self.camera.delete()
        self.assertEqual(Image.objects.count(), count_before - 1)
        self.assertFalse(Image.objects.filter(pk=self.image.pk).exists())


class ImageSerializerTest(TestCase):
    """
    Test for image serializer
    """
    def setUp(self):
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
        serializer = ImageSerializer(instance=self.image)
        self.assertEqual(
            set(serializer.data.keys()),
            {'id', 'camera', 'motion_event', 'filepath', 'filesize', 'created_at'}
        )

    def test_serializer_camera_derived_from_motion(self):
        serializer = ImageSerializer(instance=self.image)
        self.assertEqual(serializer.data['camera'], self.camera.id)

    def test_serializer_valid_data(self):
        data = {
            "motion_event": self.motion_event.id,
            "filepath": "http://example.com/images/capture_002.jpg",
            "filesize": 204800
        }
        serializer = ImageSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_serializer_invalid_filepath(self):
        data = {
            "motion_event": self.motion_event.id,
            "filepath": "not-a-valid-url"
        }
        serializer = ImageSerializer(data=data)
        self.assertFalse(serializer.is_valid())


class ImageAPITest(APITestCase):

    def setUp(self):
        self.camera = Camera.objects.create(
            address="http://192.168.1.100:8080/video",
            resolution="1920x1080",
            fps=30,
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
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), Image.objects.count())
        self.assertIn(self.image.pk, [item["id"] for item in response.data])

    def test_get_image_detail(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['filepath'], self.image.filepath)

    def test_get_image_includes_camera(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['camera'], self.camera.id)

    def test_create_image(self):
        count_before = Image.objects.count()
        data = {
            "motion_event": self.motion_event.id,
            "filepath": "http://example.com/images/capture_002.jpg",
            "filesize": 204800
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Image.objects.count(), count_before + 1)

    def test_update_image(self):
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
        data = {"filesize": 1024000}
        response = self.client.patch(self.detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.image.refresh_from_db()
        self.assertEqual(self.image.filesize, 1024000)

    def test_delete_image(self):
        count_before = Image.objects.count()
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Image.objects.count(), count_before - 1)
        self.assertFalse(Image.objects.filter(pk=self.image.pk).exists())

    def test_get_nonexistent_image(self):
        url = reverse('image-detail', kwargs={'pk': 9999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_image_invalid_motion_event(self):
        data = {
            "motion_event": 9999,
            "filepath": "http://example.com/images/capture.jpg"
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_camera_images_via_nested_route(self):
        url = reverse('camera-images', kwargs={'pk': self.camera.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_motion_images_via_nested_route(self):
        url = reverse('motion-images', kwargs={'pk': self.motion_event.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
