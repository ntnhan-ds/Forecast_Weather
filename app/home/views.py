from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from dotenv import load_dotenv
import os
import requests

# Create your views here.


def get_home(request):
    api_url_present_day = "http://localhost:8888/api/present_day"
    api_url_forecast_4_days = "http://localhost:8888/api/forecast_4_days"

    response_present_day = requests.get(api_url_present_day)
    present_day_data = response_present_day.json()

    response_forecast_4_days = requests.get(api_url_forecast_4_days)
    forecast_4_days_data = response_forecast_4_days.json()

    if response_present_day.status_code != 200 or "error" in present_day_data:
        present_day_data = {
            "city": "",
            "updated_time": "",
            "temperature_c": "",
            "wind_speed_kph": "",
            "humidity": "",
            "icon": "",
            "condition": "",
        }

    if response_forecast_4_days.status_code != 200 or "error" in forecast_4_days_data:
        forecast_4_days_data = {"forecast": []}

    # print(present_day_data)
    # print(forecast_4_days_data["forecast"])
    return render(
        request,
        "home/home.html",
        {
            "present_day_data": present_day_data,
            "forecast_4_days_data": forecast_4_days_data["forecast"],
        },
    )


def get_location(request):
    if request.method == "GET":
        latitude = request.GET.get("latitude")
        longitude = request.GET.get("longitude")

        return JsonResponse({"latitude": latitude, "longitude": longitude})
