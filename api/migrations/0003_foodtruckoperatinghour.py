# Generated by Django 4.2.7 on 2023-11-29 15:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0002_alter_foodtruck_noi_sent_alter_foodtruck_x_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="FoodTruckOperatingHour",
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
                ("day", models.CharField(max_length=9)),
                ("open_time", models.TimeField()),
                ("close_time", models.TimeField()),
                (
                    "food_truck",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="operating_hours",
                        to="api.foodtruck",
                    ),
                ),
            ],
        ),
    ]
