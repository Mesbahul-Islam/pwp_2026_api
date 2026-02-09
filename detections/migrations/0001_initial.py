from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("images", "0001_initial"),
        ("motions", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Detection",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("object_class", models.CharField(max_length=100)),
                ("confidence", models.FloatField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "image",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="detections",
                        to="images.image",
                    ),
                ),
                (
                    "motion_event",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="detections",
                        to="motions.motionevent",
                    ),
                ),
            ],
        ),
    ]
