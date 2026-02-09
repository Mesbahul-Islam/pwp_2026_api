from django.db import migrations


CAMERA_ADDRESS_PREFIX = "http://example.com/cameras/"
IMAGE_FILEPATH_PREFIX = "http://example.com/media/"


def seed_example_data(apps, schema_editor):
    Camera = apps.get_model("cameras", "Camera")
    MotionEvent = apps.get_model("motions", "MotionEvent")
    Image = apps.get_model("images", "Image")
    Detection = apps.get_model("detections", "Detection")
    Alert = apps.get_model("alerts", "Alert")

    resolutions = ["1280x720", "1920x1080", "3840x2160"]
    cameras = []
    for i in range(10):
        cameras.append(
            Camera(
                address=f"{CAMERA_ADDRESS_PREFIX}{i + 1}",
                resolution=resolutions[i % len(resolutions)],
                fps=25 + (i % 3) * 5,
                motion_sensitivity=0.2 + (i * 0.02),
                status="active" if i % 2 == 0 else "inactive",
            )
        )
    Camera.objects.bulk_create(cameras)
    cameras = list(Camera.objects.filter(address__startswith=CAMERA_ADDRESS_PREFIX))

    motion_events = []
    for i, camera in enumerate(cameras):
        motion_events.append(
            MotionEvent(
                camera=camera,
                duration=2.5 + (i * 0.5),
                threshold=0.3 + (i * 0.05),
            )
        )
    MotionEvent.objects.bulk_create(motion_events)
    motion_events = list(MotionEvent.objects.filter(camera__in=cameras))

    images = []
    for i, (camera, motion_event) in enumerate(zip(cameras, motion_events)):
        images.append(
            Image(
                camera=camera,
                motion_event=motion_event,
                filepath=f"{IMAGE_FILEPATH_PREFIX}{i + 1}.jpg",
                filesize=150000 + (i * 2500),
            )
        )
    Image.objects.bulk_create(images)
    images = list(Image.objects.filter(filepath__startswith=IMAGE_FILEPATH_PREFIX))

    object_classes = [
        "person",
        "car",
        "bicycle",
        "dog",
        "cat",
        "truck",
        "bus",
        "motorcycle",
        "backpack",
        "umbrella",
    ]
    detections = []
    for i, (motion_event, image) in enumerate(zip(motion_events, images)):
        detections.append(
            Detection(
                motion_event=motion_event,
                image=image,
                object_class=object_classes[i],
                confidence=0.55 + (i * 0.03),
            )
        )
    Detection.objects.bulk_create(detections)
    detections = list(Detection.objects.filter(image__in=images))

    alerts = []
    for i, detection in enumerate(detections):
        alerts.append(
            Alert(
                detection=detection,
                message=(
                    f"Detected {detection.object_class} with confidence "
                    f"{detection.confidence:.2f}"
                ),
                delivered=i % 2 == 0,
            )
        )
    Alert.objects.bulk_create(alerts)


def unseed_example_data(apps, schema_editor):
    Camera = apps.get_model("cameras", "Camera")
    MotionEvent = apps.get_model("motions", "MotionEvent")
    Image = apps.get_model("images", "Image")
    Detection = apps.get_model("detections", "Detection")
    Alert = apps.get_model("alerts", "Alert")

    alerts = Alert.objects.filter(
        detection__image__filepath__startswith=IMAGE_FILEPATH_PREFIX
    )
    alerts.delete()
    Detection.objects.filter(image__filepath__startswith=IMAGE_FILEPATH_PREFIX).delete()
    Image.objects.filter(filepath__startswith=IMAGE_FILEPATH_PREFIX).delete()
    MotionEvent.objects.filter(camera__address__startswith=CAMERA_ADDRESS_PREFIX).delete()
    Camera.objects.filter(address__startswith=CAMERA_ADDRESS_PREFIX).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("alerts", "0001_initial"),
        ("cameras", "0001_initial"),
        ("motions", "0001_initial"),
        ("images", "0001_initial"),
        ("detections", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_example_data, unseed_example_data),
    ]
