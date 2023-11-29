import csv
from django.core.management.base import BaseCommand
from api.models import FoodTruck
import django
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "food_trucks_locator.settings")
django.setup()


class Command(BaseCommand):
    help = "Load a list of food trucks from a CSV file"

    def add_arguments(self, parser):
        parser.add_argument("csv_file", type=str)

    def handle(self, *args, **kwargs):
        file_path = kwargs["csv_file"]
        with open(file_path, mode="r", encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)
            for row in reader:
                location_id = row["locationid"]
                latitude = float(row["Latitude"])
                longitude = float(row["Longitude"])

                # Check for duplicate by location ID, latitude, and longitude
                if not FoodTruck.objects.filter(
                    locationid=location_id, latitude=latitude, longitude=longitude
                ).exists():
                    FoodTruck.objects.create(**row)

        self.stdout.write(self.style.SUCCESS("Successfully loaded food truck data"))
