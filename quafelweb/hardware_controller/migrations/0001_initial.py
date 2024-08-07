# Generated by Django 5.0.6 on 2024-07-16 12:11

import uuid

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="HardwareProfile",
            fields=[
                (
                    "uuid",
                    models.UUIDField(
                        default=uuid.uuid4, primary_key=True, serialize=False
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("description", models.CharField(max_length=1000)),
                ("protocol", models.CharField(max_length=100)),
                ("ip_addr", models.GenericIPAddressField(default="240.0.0.0")),
                ("port_addr", models.IntegerField(default=0)),
                ("archived", models.BooleanField(default=False)),
            ],
        ),
    ]
