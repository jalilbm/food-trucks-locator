from django.urls import path
from .views import FoodTruckListView

urlpatterns = [
    path("food-trucks/", FoodTruckListView.as_view(), name="food-truck-list"),
]
