from django.contrib import admin

from .models import Earthquake, EarthquakeEvent


@admin.register(Earthquake)
class EarthquakeAdmin(admin.ModelAdmin):
    list_display = ('earthquake_no', 'epicenter', 'magnitude_value', 'date', 'time')
    search_fields = ('earthquake_no', 'epicenter')
    list_filter = ('date', 'magnitude_value')

@admin.register(EarthquakeEvent)
class EarthquakeEventAdmin(admin.ModelAdmin):
    list_display = ('event_id', 'earthquake', 'city', 'area_intensity')
    search_fields = ('event_id', 'city')
    list_filter = ('city', 'area_intensity')