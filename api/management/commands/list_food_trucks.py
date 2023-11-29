from django.core.management.base import BaseCommand, CommandError
from api.utils import (
    get_top_ten_closet_trucks_by_straight_distance,
    get_top_five_closet_trucks_by_walking_time,
)
from api.serializers import FoodTruckSerializer
from rich.console import Console
from rich.table import Table
import traceback


class Command(BaseCommand):
    help = "List the top 5 closest food trucks based on location and optionally time and timezone"
    console = Console()

    def add_arguments(self, parser):
        parser.add_argument("latitude", type=float, help="Latitude of the location")
        parser.add_argument("longitude", type=float, help="Longitude of the location")
        parser.add_argument(
            "--time", type=str, help="Time in format YYYY-MM-DD HH:MM", default=None
        )
        parser.add_argument("--timezone", type=str, help="Timezone", default=None)

    def handle(self, *args, **kwargs):
        latitude = kwargs["latitude"]
        longitude = kwargs["longitude"]
        user_time = kwargs["time"]
        user_timezone = kwargs["timezone"]

        # Ensure that if time is provided, timezone is also provided
        if user_time and not user_timezone:
            raise CommandError("Timezone is required when time is provided.")

        try:
            top_ten_trucks = get_top_ten_closet_trucks_by_straight_distance(
                latitude, longitude, user_time, user_timezone
            )
            top_five_trucks = get_top_five_closet_trucks_by_walking_time(
                latitude, longitude, top_ten_trucks
            )

            serializer = FoodTruckSerializer(
                [truck["truck_details"] for truck in top_five_trucks], many=True
            )

            # Create a Rich table
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Applicant", style="dim")
            table.add_column("Address")
            table.add_column("Food Items")
            table.add_column("Distance")
            table.add_column("Duration")

            for truck in top_five_trucks:
                truck_details = truck["truck_details"]
                gmaps_response = truck["gmaps_response"]
                distance = gmaps_response["rows"][0]["elements"][0]["distance"]["text"]
                duration = gmaps_response["rows"][0]["elements"][0]["duration"]["text"]

                table.add_row(
                    truck_details.applicant,
                    truck_details.address,
                    truck_details.food_items,
                    distance,
                    duration,
                )
            self.console.print(table)
        except Exception as e:
            self.console.print(traceback.format_exc())
            self.console.print(f"[red]An error occurred: {e}[/red]")
