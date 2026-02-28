"""
Tests for the motions app.
Tests cover models, serializers, and API endpoints.
"""
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from cameras.models import Camera
from .models import MotionEvent
from .serializers import MotionEventSerializer


class MotionEventModelTest(TestCase):
    """Test cases for the MotionEvent model."""

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

    def test_motion_event_creation(self):
        """Test that a motion event can be created."""
        self.assertEqual(self.motion_event.camera, self.camera)
        self.assertEqual(self.motion_event.duration, 5.5)
        self.assertEqual(self.motion_event.threshold, 0.3)

    def test_motion_event_str_representation(self):
        """Test the string representation of a motion event."""
        self.assertIn("Motion detected by", str(self.motion_event))

    def test_motion_event_auto_timestamp(self):
        """Test that timestamp is auto-generated."""
        self.assertIsNotNone(self.motion_event.timestamp)

    def test_motion_event_auto_created_at(self):
        """Test that created_at is auto-generated."""
        self.assertIsNotNone(self.motion_event.created_at)

    def test_motion_event_nullable_fields(self):
        """Test that duration and threshold can be null."""
        motion = MotionEvent.objects.create(camera=self.camera)
        self.assertIsNone(motion.duration)
        self.assertIsNone(motion.threshold)

    def test_motion_event_camera_cascade_delete(self):
        """Test that motion events are deleted when camera is deleted."""
        camera_id = self.camera.id
        self.camera.delete()
        self.assertEqual(
            MotionEvent.objects.filter(camera_id=camera_id).count(),
            0
        )


class MotionEventSerializerTest(TestCase):
    """Test cases for the MotionEvent serializer."""

    def setUp(self):
        """Set up test data."""
        self.camera = Camera.objects.create(
            address="http://192.168.1.100:8080/video",
            resolution="1920x1080"
        )
        self.motion_event = MotionEvent.objects.create(
            camera=self.camera,
            duration=5.5,
            threshold=0.3
        )

    def test_serializer_contains_expected_fields(self):
        """Test that serializer contains all expected fields."""
        serializer = MotionEventSerializer(instance=self.motion_event)
        self.assertEqual(
            set(serializer.data.keys()),
            {'id', 'camera', 'timestamp', 'duration', 'threshold', 'created_at'}
        )

    def test_serializer_valid_data(self):
        """Test serializer with valid data."""
        data = {
            "camera": self.camera.id,
            "duration": 10.0,
            "threshold": 0.5
        }
        serializer = MotionEventSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_serializer_read_only_fields(self):
        """Test that timestamp and created_at are read-only."""
        serializer = MotionEventSerializer()
        self.assertIn('timestamp', serializer.Meta.read_only_fields)
        self.assertIn('created_at', serializer.Meta.read_only_fields)


class MotionEventAPITest(APITestCase):
    """Test cases for the MotionEvent API endpoints."""

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
        self.list_url = reverse('motion-list')
        self.detail_url = reverse('motion-detail', kwargs={'pk': self.motion_event.pk})

    def test_get_motion_list(self):
        """Test GET request to list all motion events."""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_motion_detail(self):
        """Test GET request to retrieve a specific motion event."""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['camera'], self.camera.id)

    def test_create_motion_event(self):
        """Test POST request to create a new motion event."""
        data = {
            "camera": self.camera.id,
            "duration": 10.0,
            "threshold": 0.5
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(MotionEvent.objects.count(), 2)

    def test_update_motion_event(self):
        """Test PUT request to update a motion event."""
        data = {
            "camera": self.camera.id,
            "duration": 15.0,
            "threshold": 0.6
        }
        response = self.client.put(self.detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.motion_event.refresh_from_db()
        self.assertEqual(self.motion_event.duration, 15.0)

    def test_partial_update_motion_event(self):
        """Test PATCH request to partially update a motion event."""
        data = {"duration": 20.0}
        response = self.client.patch(self.detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.motion_event.refresh_from_db()
        self.assertEqual(self.motion_event.duration, 20.0)

    def test_delete_motion_event(self):
        """Test DELETE request to remove a motion event."""
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(MotionEvent.objects.count(), 0)

    def test_get_nonexistent_motion_event(self):
        """Test GET request for a motion event that doesn't exist."""
        url = reverse('motion-detail', kwargs={'pk': 9999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_motion_event_invalid_camera(self):
        """Test POST request with invalid camera ID."""
        data = {
            "camera": 9999,
            "duration": 10.0
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_motion_images_empty(self):
        """Test GET request for motion images when none exist."""
        url = reverse('motion-images', kwargs={'pk': self.motion_event.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
