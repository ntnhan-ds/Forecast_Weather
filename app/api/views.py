from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from dotenv import load_dotenv
import os
import requests
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Create your views here.

load_dotenv()
api_key = os.getenv("weather_api_key")
email = os.getenv("email")
password = os.getenv("password")

api_v1_url = "http://api.weatherapi.com/v1/"


@csrf_exempt
def send_weather(request):
    if request.method == "POST":
        data = json.loads(request.body.decode("utf-8"))

        latitude = data.get("latitude")
        longitude = data.get("longitude")
        city = get_city_from_location(latitude, longitude)

        data_weather = get_weather_on_day(city)

        receiver_email = data.get("email")
        sender_email = email
        sender_password = password

        # Create MIMEMultipart object
        msg = MIMEMultipart()

        msg["From"] = sender_email
        msg["To"] = receiver_email
        msg["Subject"] = "Information Weather"

        data_sender = f"""
            City: {data_weather['city']}
            Time update: {data_weather['updated_time']}
            Temperature: {data_weather['temperature_c']} °C
            Humidity: {data_weather['humidity']} %
            Wind speed: {data_weather['wind_speed_kph']} km/h
            Conditional: {data_weather['condition']} 
        """

        # Nội dung email
        body = f"Hello, this is an email from Weather today.\n\n {data_sender} \n\n Have a nice day!"
        msg.attach(MIMEText(body, "plain"))
        # Server
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())

        server.quit()

    return JsonResponse({"message": "Email sent successfully!"})


def get_city_from_location(lat, lon):
    url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json&accept-language=en"
    headers = {"User-Agent": "YourAppName/1.0 (your-email@example.com)"}
    response = requests.get(url, headers=headers)

    # print(response.content)

    try:
        data = json.loads(response.content.decode("utf-8"))
    except json.JSONDecodeError:
        print("Error decoding JSON from Nominatim API")
        return None

    print(data)
    if "address" in data:
        address = data["address"]
        city = address.get(
            "city", address.get("town", address.get("village", "Unknown"))
        )
        return city
    else:
        print("Address not found in response data")
        return None


def get_weather_on_day(city):
    current_weather_url = api_v1_url + f"current.json?key={api_key}&q={city}"
    response = requests.get(current_weather_url)
    data = response.json()
    # print(data)
    if "location" in data and "current" in data:
        location = data["location"]
        current = data["current"]
        weather_info = {
            "city": location["name"],
            "updated_time": current["last_updated"],
            "temperature_c": current["temp_c"],
            "humidity": current["humidity"],
            "wind_speed_kph": current["wind_kph"] / 3.6,
            "condition": current["condition"]["text"],
            "icon": current["condition"]["icon"],
        }
    return weather_info


@csrf_exempt
def get_weather_present_day(request):
    if request.method == "GET":
        city = "London"

        weather_info = get_weather_on_day(city)
        return JsonResponse(weather_info)

    elif request.method == "POST":
        data = json.loads(request.body.decode("utf-8"))
        city = data.get("city")
        if city is None:
            latitude = data.get("latitude")
            longitude = data.get("longitude")
            city = get_city_from_location(latitude, longitude)

        weather_info = get_weather_on_day(city)
        return JsonResponse(weather_info)


def get_weather_forecast(city):
    forecast_weather_url = f"{api_v1_url}forecast.json?key={api_key}&q={city}&days=4"
    response = requests.get(forecast_weather_url)
    data = response.json()

    if "location" in data and "forecast" in data:
        location = data["location"]
        current = data["current"]
        forecast = data["forecast"]["forecastday"]
        weather_info = {
            "city": location["name"],
            "forecast": [],
        }
        for day in forecast:
            weather_info["forecast"].append(
                {
                    "date": day["date"],
                    "temperature_c": day["day"]["avgtemp_c"],
                    "wind_speed_kph": day["day"]["maxwind_kph"] / 3.6,
                    "icon": day["day"]["condition"]["icon"],
                    "humidity": day["day"]["avghumidity"],
                }
            )
        return weather_info
    else:
        return None


@csrf_exempt
def forecasting_weather_next_4_days(request):
    if request.method == "GET":
        city = "London"
        weather_info = get_weather_forecast(city)
        return JsonResponse(weather_info)

    elif request.method == "POST":
        data = json.loads(request.body.decode("utf-8"))
        city = data.get("city")
        # print(data)
        if city is None:
            latitude = data.get("latitude")
            longitude = data.get("longitude")
            city = get_city_from_location(latitude, longitude)

        weather_info = get_weather_forecast(city)
        return JsonResponse(weather_info)
