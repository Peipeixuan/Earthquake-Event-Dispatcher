from django.db import models


class Earthquake(models.Model):
    earthquake_no = models.CharField(max_length=20, primary_key=True)  # Primary key
    report_content = models.TextField()
    report_image_uri = models.URLField(null=True, blank=True)
    shakemap_image_uri = models.URLField(null=True, blank=True)
    epicenter = models.CharField(max_length=255)
    epicenter_latitude = models.FloatField()
    epicenter_longitude = models.FloatField()
    magnitude_type = models.CharField(max_length=50)
    magnitude_value = models.FloatField()
    date = models.DateField()
    time = models.TimeField()
    taipei = models.CharField(max_length=10, null=True, blank=True)
    taichung = models.CharField(max_length=10, null=True, blank=True)
    tainan = models.CharField(max_length=10, null=True, blank=True)
    taitung = models.CharField(max_length=10, null=True, blank=True)

    def __str__(self):
        return f"Earthquake {self.earthquake_no}"

class EarthquakeEvent(models.Model):
    event_id = models.CharField(max_length=50, primary_key=True)  # e.g., {earthquake_no}-tp
    earthquake = models.ForeignKey('Earthquake', on_delete=models.CASCADE)
    city = models.CharField(max_length=50)
    area_intensity = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.event_id} ({self.city})"