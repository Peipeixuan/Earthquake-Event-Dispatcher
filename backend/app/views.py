import logging

import requests
from django.http import HttpResponse
from django.shortcuts import render

from .models import Earthquake, EarthquakeEvent

logger = logging.getLogger(__name__)


def homepage(request):
    return render(request, "homepage.html")


def fetch_earthquake_data(request=None):
    # API URL and key
    url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/E-A0015-001"
    params = {
        "Authorization": "CWA-0D5559F3-F35F-4B30-8A11-B532CA021040",
        "limit": 1,  # Fetch only the latest earthquake report
    }

    # Make the API request
    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()  # Parse the JSON response
        earthquake_list = data.get("records", {}).get("Earthquake", [])

        if earthquake_list:
            latest_report = earthquake_list[0]
            earthquake_no = latest_report.get("EarthquakeNo", "N/A")

            # Extract data
            earthquake_data = {
                "earthquake_no": earthquake_no,
                "report_content": latest_report.get("ReportContent", "N/A"),
                "report_image_uri": latest_report.get("ReportImageURI", None),
                "shakemap_image_uri": latest_report.get("ShakemapImageURI", None),
                "epicenter": latest_report.get("EarthquakeInfo", {}).get("Epicenter", {}).get("Location", "N/A"),
                "epicenter_latitude": latest_report.get("EarthquakeInfo", {}).get("Epicenter", {}).get("EpicenterLatitude", 0.0),
                "epicenter_longitude": latest_report.get("EarthquakeInfo", {}).get("Epicenter", {}).get("EpicenterLongitude", 0.0),
                "magnitude_type": latest_report.get("EarthquakeInfo", {}).get("EarthquakeMagnitude", {}).get("MagnitudeType", "N/A"),
                "magnitude_value": latest_report.get("EarthquakeInfo", {}).get("EarthquakeMagnitude", {}).get("MagnitudeValue", 0.0),
                "date": latest_report.get("EarthquakeInfo", {}).get("OriginTime", "").split(" ")[0],
                "time": latest_report.get("EarthquakeInfo", {}).get("OriginTime", "").split(" ")[1],
                "taipei": "N/A",
                "taichung": "N/A",
                "tainan": "N/A",
                "taitung": "N/A",
            }

            # Update intensity data for specific cities
            intensity_data = latest_report.get("Intensity", {}).get("ShakingArea", [])
            for area in intensity_data:
                city_name = area.get("CountyName", "")
                if city_name == "臺北市":
                    earthquake_data["taipei"] = area.get("AreaIntensity", "N/A")
                elif city_name == "臺中市":
                    earthquake_data["taichung"] = area.get("AreaIntensity", "N/A")
                elif city_name == "臺南市":
                    earthquake_data["tainan"] = area.get("AreaIntensity", "N/A")
                elif city_name == "臺東縣":
                    earthquake_data["taitung"] = area.get("AreaIntensity", "N/A")

            # Save or update the earthquake record in the database
            earthquake, created = Earthquake.objects.update_or_create(
                earthquake_no=earthquake_no,
                defaults=earthquake_data
            )

            if created:
                logger.info(f"New earthquake data saved: {earthquake_no}")
            else:
                logger.info(f"Earthquake data updated: {earthquake_no}")

            # Create or update EarthquakeEvent records
            city_mapping = {
                "taipei": "tp",
                "taichung": "tc",
                "tainan": "tn",
                "taitung": "tt",
            }

            for city, suffix in city_mapping.items():
                area_intensity = earthquake_data[city]
                if area_intensity != "N/A":
                    event_id = f"{earthquake_no}-{suffix}"
                    EarthquakeEvent.objects.update_or_create(
                        event_id=event_id,
                        defaults={
                            "earthquake": earthquake,
                            "city": city,
                            "area_intensity": area_intensity,
                        }
                    )
                    logger.info(f"Earthquake event saved/updated: {event_id}")

            # Return an HTTP response if accessed via a browser
            if request is not None:
                return HttpResponse(f"Earthquake data processed: {earthquake_no}")

        else:
            logger.info("No earthquake data available from the API.")
            if request is not None:
                return HttpResponse("No earthquake data available from the API.")

    else:
        logger.error(f"Failed to fetch data from the API. Status code: {response.status_code}")
        if request is not None:
            return HttpResponse(f"Failed to fetch data from the API. Status code: {response.status_code}")

    # If called by the scheduler, return nothing
    if request is None:
        return