from django.db import models


class FoodTruck(models.Model):
    location_id = models.CharField(max_length=100, unique=True)
    applicant = models.CharField(max_length=255)
    facility_type = models.CharField(max_length=100)
    cnn = models.CharField(max_length=100)
    location_description = models.TextField()
    address = models.CharField(max_length=255)
    block_lot = models.CharField(max_length=100)
    block = models.CharField(max_length=100)
    lot = models.CharField(max_length=100)
    permit = models.CharField(max_length=100)
    status = models.CharField(max_length=100)
    food_items = models.TextField()
    x = models.FloatField(null=True)
    y = models.FloatField(null=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    schedule = models.TextField()
    days_hours = models.CharField(max_length=100, null=True)
    noi_sent = models.CharField(null=True, max_length=100)
    approved = models.DateTimeField(null=True, blank=True)
    received = models.DateTimeField(null=True, blank=True)
    prior_permit = models.IntegerField()
    expiration_date = models.DateTimeField(null=True, blank=True)
    location = models.TextField()
    fire_prevention_districts = models.IntegerField(null=True, blank=True)
    police_districts = models.IntegerField(null=True, blank=True)
    supervisor_districts = models.IntegerField(null=True, blank=True)
    zip_codes = models.IntegerField(null=True, blank=True)
    neighborhoods = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.applicant


class FoodTruckOperatingHour(models.Model):
    food_truck = models.ForeignKey(
        FoodTruck, related_name="operating_hours", on_delete=models.CASCADE
    )
    day = models.CharField(max_length=9)  # For example, 'Monday', 'Tuesday', etc.
    open_time = models.TimeField()
    close_time = models.TimeField()

    def __str__(self):
        return f"{self.food_truck.applicant} - {self.day}: {self.open_time.strftime('%I:%M %p')} - {self.close_time.strftime('%I:%M %p')}"
