from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path("send_weather", views.send_weather),
    path("present_day", views.get_weather_present_day),
    path("forecast_4_days", views.forecasting_weather_next_4_days),
]
