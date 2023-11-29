import csv
from django.core.management.base import BaseCommand
from api.models import FoodTruck, FoodTruckOperatingHour
from datetime import datetime
from django.utils import timezone


class Command(BaseCommand):
    help = "Load a list of food trucks from a CSV file"

    def add_arguments(self, parser):
        parser.add_argument("csv_file", type=str)

    def handle(self, *args, **kwargs):
        file_path = kwargs["csv_file"]

        # Function to parse datetime in AM/PM format
        def parse_datetime(datetime_str):
            if datetime_str:
                try:
                    naive_datetime = datetime.strptime(
                        datetime_str, "%m/%d/%Y %I:%M:%S %p"
                    )
                    return timezone.make_aware(
                        naive_datetime, timezone.get_default_timezone()
                    )
                except ValueError:
                    self.stdout.write(
                        self.style.ERROR("Invalid datetime format detected.")
                    )
            return None

        # Function to parse date without time
        def parse_date(datetime_str):
            if datetime_str:
                try:
                    naive_datetime = datetime.strptime(datetime_str, "%Y%m%d")
                    return timezone.make_aware(
                        naive_datetime, timezone.get_default_timezone()
                    )
                except ValueError:
                    self.stdout.write(self.style.ERROR("Invalid date format detected."))
            return None

        # Function to parse day range like 'Mo-We'
        def parse_day_range(day_range_str):
            days_mapping = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]
            start_day, end_day = day_range_str.split("-")
            start_index = days_mapping.index(start_day)
            end_index = days_mapping.index(end_day)
            return days_mapping[start_index : end_index + 1]

        # Function to parse operating hours
        def parse_hours(hours_str):
            days_mapping = {
                "Mo": "Monday",
                "Tu": "Tuesday",
                "We": "Wednesday",
                "Th": "Thursday",
                "Fr": "Friday",
                "Sa": "Saturday",
                "Su": "Sunday",
            }

            day_groups = hours_str.split(";")
            operating_hours = []

            for group in day_groups:
                days, times = group.split(":")
                time_ranges = times.split("/")
                for time_range in time_ranges:
                    open_time, close_time = time_range.split("-")
                    if "-" in days:
                        day_range = parse_day_range(days)
                        for day_code in day_range:
                            operating_hours.append(
                                {
                                    "day": days_mapping[day_code],
                                    "open_time": datetime.strptime(
                                        open_time.strip(), "%I%p"
                                    ).time(),
                                    "close_time": datetime.strptime(
                                        close_time.strip(), "%I%p"
                                    ).time(),
                                }
                            )
                    else:
                        for day_code in days.split("/"):
                            operating_hours.append(
                                {
                                    "day": days_mapping[day_code],
                                    "open_time": datetime.strptime(
                                        open_time.strip(), "%I%p"
                                    ).time(),
                                    "close_time": datetime.strptime(
                                        close_time.strip(), "%I%p"
                                    ).time(),
                                }
                            )

            return operating_hours

        # Read CSV and populate database
        try:
            with open(file_path, mode="r", encoding="utf-8-sig") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    # Check for duplicates and valid latitude/longitude
                    if (
                        not FoodTruck.objects.filter(
                            location_id=row["locationid"],
                            latitude=row["Latitude"],
                            longitude=row["Longitude"],
                        ).exists()
                        and float(row.get("Latitude")) != 0
                        and float(row.get("Longitude")) != 0
                    ):
                        # Map CSV row to FoodTruck model fields
                        mapped_row = {
                            "location_id": row.get("locationid"),
                            "applicant": row.get("Applicant"),
                            "facility_type": row.get("FacilityType"),
                            "cnn": row.get("cnn"),
                            "location_description": row.get("LocationDescription"),
                            "address": row.get("Address"),
                            "block_lot": row.get("blocklot"),
                            "block": row.get("block"),
                            "lot": row.get("lot"),
                            "permit": row.get("permit"),
                            "status": row.get("Status"),
                            "food_items": row.get("FoodItems"),
                            "x": float(row.get("X")) if row.get("X") else None,
                            "y": float(row.get("Y")) if row.get("Y") else None,
                            "latitude": float(row.get("Latitude")),
                            "longitude": float(row.get("Longitude")),
                            "schedule": row.get("Schedule"),
                            "days_hours": row.get("dayshours")
                            if row.get("dayshours")
                            else None,
                            "noi_sent": row.get("NOISent"),
                            "approved": parse_datetime(row.get("Approved")),
                            "received": parse_date(row.get("Received")),
                            "prior_permit": int(row.get("PriorPermit")),
                            "expiration_date": parse_datetime(
                                row.get("ExpirationDate")
                            ),
                            "location": row.get("Location"),
                            "fire_prevention_districts": int(
                                row.get("Fire Prevention Districts")
                            )
                            if row.get("Fire Prevention Districts")
                            else None,
                            "police_districts": int(row.get("Police Districts"))
                            if row.get("Police Districts")
                            else None,
                            "supervisor_districts": int(row.get("Supervisor Districts"))
                            if row.get("Supervisor Districts")
                            else None,
                            "zip_codes": int(row.get("Zip Codes"))
                            if row.get("Zip Codes")
                            else None,
                            "neighborhoods": row.get("Neighborhoods (old)"),
                        }
                        # Create FoodTruck instance
                        food_truck_instance = FoodTruck.objects.create(**mapped_row)

                        # Parse and create operating hours
                        if row.get("dayshours"):
                            hours_data = parse_hours(row["dayshours"])
                            for hour_data in hours_data:
                                FoodTruckOperatingHour.objects.create(
                                    food_truck=food_truck_instance,
                                    day=hour_data["day"],
                                    open_time=hour_data["open_time"],
                                    close_time=hour_data["close_time"],
                                )

            self.stdout.write(self.style.SUCCESS("Successfully loaded food truck data"))
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"File not found: {file_path}"))
        except csv.Error as e:
            self.stdout.write(self.style.ERROR(f"CSV error: {e}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Unexpected error: {e}"))
