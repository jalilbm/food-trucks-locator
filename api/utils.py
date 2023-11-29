from django.contrib.gis.measure import Distance, D
from geopy.distance import distance
from .models import FoodTruck, FoodTruckOperatingHour
from food_trucks_locator.settings import gmaps
from datetime import datetime
import pytz
from concurrent.futures import ThreadPoolExecutor


def calculate_straight_distance_between_two_points(lat_1, long_1, lat_2, long_2):
    """
    Calculate the straight-line distance between two points.
    """
    return Distance(m=distance((lat_1, long_1), (lat_2, long_2)).meters)


def get_top_ten_closet_trucks_by_straight_distance(lat, long, user_time, user_timezone):
    """
    Get the top 10 closest trucks by straight-line distance.
    Considers truck's open status if user_time is provided.
    """
    trucks_with_straight_distance = []
    if user_time:
        # Localize user time to the specified timezone and convert to UTC
        # This is necessary for time comparison in a standardized format
        try:
            user_timezone_aware = pytz.timezone(user_timezone).localize(
                datetime.strptime(user_time, "%Y-%m-%dT%H:%M")
            )
            user_datetime = user_timezone_aware.astimezone(pytz.utc)
        except Exception as e:
            raise ValueError("Invalid time or timezone.") from e

        # Loop through all FoodTruck objects
        for truck in FoodTruck.objects.all():
            # If user time is provided, check if the truck is open at that time
            if is_truck_open_now(truck, user_datetime):
                trucks_with_straight_distance.append(
                    (
                        truck,
                        calculate_straight_distance_between_two_points(
                            lat,
                            long,
                            float(truck.latitude),
                            float(truck.longitude),
                        ),
                    )
                )
    else:
        for truck in FoodTruck.objects.all():
            trucks_with_straight_distance.append(
                (
                    truck,
                    calculate_straight_distance_between_two_points(
                        lat,
                        long,
                        float(truck.latitude),
                        float(truck.longitude),
                    ),
                )
            )

    # Sort the list of trucks by their calculated straight-line distance
    trucks_with_straight_distance.sort(key=lambda x: x[1])
    # Return the top 10 closest trucks
    return [t[0] for t in trucks_with_straight_distance[:10]]


def get_walking_time_data(truck, lat, long):
    """
    Fetches walking time data from Google Maps API for a specific truck.
    """
    try:
        # Perform a request to Google Maps API for walking directions
        # and return the response along with truck details
        return {
            "truck_details": truck,
            "gmaps_response": gmaps.distance_matrix(
                (lat, long), (truck.latitude, truck.longitude), mode="walking"
            ),
        }
    except Exception as e:
        # Raise an error if there's an issue with the API call
        raise ConnectionError("Error connecting to Google Maps API.") from e


def get_top_five_closet_trucks_by_walking_time(lat, long, trucks):
    """
    Determines the top 5 closest food trucks based on walking time.
    """
    # Use a thread pool to make concurrent API calls for each truck
    with ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(get_walking_time_data, truck, lat, long) for truck in trucks
        ]
        # Retrieve the results from all the futures
        results = [future.result() for future in futures]

    # Sort the results based on walking duration and return the top 5
    results.sort(
        key=lambda x: x["gmaps_response"]["rows"][0]["elements"][0]["duration"]["value"]
    )
    return results[:5]


def is_truck_open_now(truck, user_datetime):
    """
    Check if the truck is open at the given datetime.
    """
    user_day = user_datetime.strftime("%A")
    user_time = user_datetime.time()
    # Filter the operating hours for the truck based on the day of the week
    operating_hours = FoodTruckOperatingHour.objects.filter(
        food_truck=truck, day=user_day
    )

    for hours in operating_hours:
        if hours.open_time <= user_time <= hours.close_time:
            # Check if current time falls within any of the operating hours
            return True
    return False
