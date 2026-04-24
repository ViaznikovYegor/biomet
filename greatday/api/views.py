import json
import requests
from datetime import datetime
from django.shortcuts import render


def interpret_weather_code(code):
    """Возвращает иконку и описание погоды по коду WMO."""
    mapping = {
        0: ("☀️", "Ясно"),
        1: ("🌤️", "Преимущественно ясно"),
        2: ("⛅", "Переменная облачность"),
        3: ("☁️", "Пасмурно"),
        45: ("🌫️", "Туман"),
        48: ("🌫️", "Туман с изморозью"),
        51: ("🌦️", "Лёгкая морось"),
        53: ("🌦️", "Морось"),
        55: ("🌧️", "Сильная морось"),
        61: ("🌧️", "Небольшой дождь"),
        63: ("🌧️", "Дождь"),
        65: ("🌧️", "Сильный дождь"),
        71: ("❄️", "Небольшой снег"),
        73: ("❄️", "Снег"),
        75: ("❄️", "Сильный снег"),
        77: ("❄️", "Снежные зёрна"),
        80: ("🌦️", "Ливень"),
        81: ("🌧️", "Сильный ливень"),
        82: ("🌧️", "Очень сильный ливень"),
        85: ("❄️", "Снегопад"),
        86: ("❄️", "Сильный снегопад"),
        95: ("⛈️", "Гроза"),
        96: ("⛈️", "Гроза с градом"),
        99: ("⛈️", "Сильная гроза с градом"),
    }
    return mapping.get(code, ("🌡️", "Неизвестно"))


def fetch_opemeteo_forecast(lat, lon, days=7):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": ",".join([
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_sum",
            "wind_speed_10m_max",
            "uv_index_max",
            "weather_code",
        ]),
        "timezone": "auto",
        "forecast_days": days,
    }

    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    daily = data.get("daily", {})

    weather_days = []
    for i in range(len(daily["time"])):
        dt = datetime.fromisoformat(daily["time"][i])
        day_name = dt.strftime("%a")[:2].upper()
        date_str = dt.strftime("%d %b").lower()

        max_temp = daily["temperature_2m_max"][i]
        min_temp = daily["temperature_2m_min"][i]
        avg_temp = round((max_temp + min_temp) / 2, 0)
        wind = daily["wind_speed_10m_max"][i]
        uv = daily["uv_index_max"][i]
        weather_code = daily["weather_code"][i]
        precipitation = daily["precipitation_sum"][i] > 0

        icon, condition = interpret_weather_code(weather_code)

        weather_days.append({
            "name": day_name,
            "date": date_str,
            "temp": avg_temp,
            "wind": wind,
            "uv": uv,
            "icon": icon,
            "condition": condition,
            "rain": precipitation,
        })

    return weather_days


def weather_ip_view(request):
    error = None
    weather_data = []
    city = "Неизвестно"

    geo = getattr(request, 'client_ip', None)

    if geo and geo.get('status') == 'success':
        lat = geo.get('lat')
        lon = geo.get('lon')
        city = f"{geo.get('city', '')}, {geo.get('country', '')}"

        try:
            weather_data = fetch_opemeteo_forecast(lat, lon)
        except Exception as e:
            error = f"Ошибка получения прогноза: {e}"
    else:
        error = "Не удалось определить город по вашему IP-адресу."

    context = {
        'city': city,
        'weather_data_json': json.dumps(weather_data, ensure_ascii=False),
        'error': error,
    }
    return render(request, 'weather.html', context)
