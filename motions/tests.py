from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from cameras.models import Camera
from .models import MotionEvent
from .serializers import MotionEventSerializer


class MotionEventModelTest(TestCase):

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

    def test_motion_event_creation(self):
        self.assertEqual(self.motion_event.camera, self.camera)
        self.assertEqual(self.motion_event.duration, 5.5)
        self.assertEqual(self.motion_event.threshold, 0.3)

    def test_motion_event_str_representation(self):
        self.assertIn("Motion detected by", str(self.motion_event))

    def test_motion_event_auto_timestamp(self):
        self.assertIsNotNone(self.motion_event.timestamp)

    def test_motion_event_auto_created_at(self):
        self.assertIsNotNone(self.motion_event.created_at)

    def test_motion_event_nullable_fields(self):
        motion = MotionEvent.objects.create(camera=self.camera)
        self.assertEqual(motion.duration, 0.0)
        self.assertEqual(motion.threshold, 0.25)

    def test_motion_event_camera_cascade_delete(self):
        camera_id = self.camera.id
        self.camera.delete()
        self.assertEqual(
            MotionEvent.objects.filter(camera_id=camera_id).count(),
            0
        )


class MotionEventSerializerTest(TestCase):

    def setUp(self):
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
        serializer = MotionEventSerializer(instance=self.motion_event)
        self.assertEqual(
            set(serializer.data.keys()),
            {'id', 'camera', 'timestamp', 'duration', 'threshold', 'created_at'}
        )

    def test_serializer_valid_data(self):
        data = {
            "camera": self.camera.id,
            "duration": 10.0,
            "threshold": 0.5
        }
        serializer = MotionEventSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_serializer_read_only_fields(self):
        serializer = MotionEventSerializer()
        self.assertIn('timestamp', serializer.Meta.read_only_fields)
        self.assertIn('created_at', serializer.Meta.read_only_fields)


class MotionEventAPITest(APITestCase):

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
        self.user = get_user_model().objects.create_user(
            username="motion_api_user",
            password="test-pass-123"
        )
        self.client.force_authenticate(user=self.user)
        self.list_url = reverse('motion-list')
        self.detail_url = reverse('motion-detail', kwargs={'pk': self.motion_event.pk})

    def test_get_motion_list(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), MotionEvent.objects.count())
        self.assertIn(self.motion_event.pk, [item["id"] for item in response.data])

    def test_get_motion_detail(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['camera'], self.camera.id)

    def test_create_motion_event(self):
        count_before = MotionEvent.objects.count()
        data = {
            "camera": self.camera.id,
            "duration": 10.0,
            "threshold": 0.5
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(MotionEvent.objects.count(), count_before + 1)

    def test_update_motion_event(self):
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
        data = {"duration": 20.0}
        response = self.client.patch(self.detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.motion_event.refresh_from_db()
        self.assertEqual(self.motion_event.duration, 20.0)

    def test_delete_motion_event(self):
        count_before = MotionEvent.objects.count()
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(MotionEvent.objects.count(), count_before - 1)
        self.assertFalse(MotionEvent.objects.filter(pk=self.motion_event.pk).exists())

    def test_get_nonexistent_motion_event(self):
        url = reverse('motion-detail', kwargs={'pk': 9999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_motion_event_invalid_camera(self):
        data = {
            "camera": 9999,
            "duration": 10.0
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_motion_images_empty(self):
        url = reverse('motion-images', kwargs={'pk': self.motion_event.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)


class MotionEventAuthenticationAPITest(APITestCase):

    def setUp(self):
        self.camera = Camera.objects.create(
            address="http://192.168.1.210:8080/video",
            resolution="1920x1080",
            fps=30,
            status="active"
        )
        self.motion_event = MotionEvent.objects.create(
            camera=self.camera,
            duration=3.5,
            threshold=0.4,
        )
        self.user = get_user_model().objects.create_user(
            username="motion_auth_user",
            password="test-pass-123"
        )
        self.list_url = reverse("motion-list")
        self.detail_url = reverse("motion-detail", kwargs={"pk": self.motion_event.pk})
        self.images_url = reverse("motion-images", kwargs={"pk": self.motion_event.pk})

    def test_anonymous_motion_endpoints_are_rejected(self):
        responses = [
            self.client.get(self.list_url),
            self.client.get(self.detail_url),
            self.client.get(self.images_url),
            self.client.post(
                self.list_url,
                {
                    "camera": self.camera.id,
                    "duration": 1.1,
                    "threshold": 0.3,
                },
                format="json",
            ),
        ]

        for response in responses:
            self.assertIn(
                response.status_code,
                [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN],
            )

    def test_authenticated_motion_list_is_allowed(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
