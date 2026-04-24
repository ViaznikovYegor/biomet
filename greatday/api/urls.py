from django.urls import path
from .views import weather_ip_view


urlpatterns = [
    path('', weather_ip_view)
]