from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import FoodTruckSerializer
import api.utils as utils
from rest_framework import status
from rest_framework.throttling import AnonRateThrottle
from django.core.cache import cache
from food_trucks_locator.settings import CACHE_TIMEOUT


class FoodTruckListView(APIView):
    throttle_classes = [AnonRateThrottle]

    def get(self, request):
        """
        Returns the top 5 closest trucks to a given `latitude` and `longitude` by walking time.
        Optionally returning only opened trucks if `time` and `timezone` are provided
        """
        latitude = request.query_params.get("latitude")
        longitude = request.query_params.get("longitude")
        user_time = request.query_params.get("time")  # Format: "YYYY-MM-DDTHH:MM"
        user_timezone = request.query_params.get("timezone")

        # Create a unique cache key
        cache_key = f"food_trucks_{latitude}_{longitude}_{user_time}_{user_timezone}"
        cached_response = cache.get(cache_key)

        if cached_response:
            return Response(cached_response)

        # Validate latitude and longitude
        if not latitude or not longitude:
            return Response(
                {"message": "Latitude and longitude parameters are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            latitude = float(latitude)
            longitude = float(longitude)
        except ValueError:
            return Response(
                {"message": "Invalid latitude or longitude values."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate time and timezone
        if user_time and not user_timezone:
            return Response(
                {"message": "When time is provided, timezone also should be provided."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Proceed if latitude and longitude are provided
        try:
            # Get the top 10 closest trucks by straight-line distance
            top_ten_closet_trucks_by_straight_distance = (
                utils.get_top_ten_closet_trucks_by_straight_distance(
                    latitude, longitude, user_time, user_timezone
                )
            )

            # From these, get the top 5 closest trucks by walking time using Google Maps API
            top_five_closet_trucks_by_walking_time = (
                utils.get_top_five_closet_trucks_by_walking_time(
                    latitude, longitude, top_ten_closet_trucks_by_straight_distance
                )
            )

            # Serialize the truck details
            serializer = FoodTruckSerializer(
                [
                    truck["truck_details"]
                    for truck in top_five_closet_trucks_by_walking_time
                ],
                many=True,
            )

            response = [
                {
                    "distance": truck["gmaps_response"]["rows"][0]["elements"][0][
                        "distance"
                    ]["text"],
                    "duration": truck["gmaps_response"]["rows"][0]["elements"][0][
                        "duration"
                    ]["text"],
                    "truck_details": serializer.data[i],
                }
                for i, truck in enumerate(top_five_closet_trucks_by_walking_time)
            ]

            cache.set(cache_key, response, timeout=CACHE_TIMEOUT)

            # Construct and return the response
            return Response(response)
        except Exception as e:
            return Response({"message": str(e)})
