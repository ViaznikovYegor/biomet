import json
import requests
from datetime import datetime
from django.shortcuts import render
from .llm_service import get_biometeo_recommendations


def interpret_weather_code(code):
    mapping = {
        0: ("☀️", "Ясно"), 1: ("🌤️", "Преимущественно ясно"), 2: ("⛅", "Переменная облачность"),
        3: ("☁️", "Пасмурно"), 45: ("🌫️", "Туман"), 51: ("🌦️", "Лёгкая морось"),
        61: ("🌧️", "Небольшой дождь"), 63: ("🌧️", "Дождь"), 65: ("🌧️", "Сильный дождь"),
        71: ("❄️", "Небольшой снег"), 80: ("🌦️", "Ливень"), 95: ("⛈️", "Гроза"),
    }
    return mapping.get(code, ("🌡️", "Неизвестно"))


def fetch_opemeteo_forecast(lat, lon):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max,uv_index_max,weather_code",
        "timezone": "auto",
        "forecast_days": 7,
    }
    resp = requests.get(url, params=params, timeout=15)
    resp.raise_for_status()
    data = resp.json()["daily"]

    weather_days = []
    for i in range(len(data["time"])):
        dt = datetime.fromisoformat(data["time"][i])
        weather_days.append({
            "name": dt.strftime("%a")[:2].upper(),
            "date": dt.strftime("%d %b").lower(),
            "temp": round((data["temperature_2m_max"][i] + data["temperature_2m_min"][i]) / 2),
            "wind": round(data["wind_speed_10m_max"][i]),
            "uv": round(data["uv_index_max"][i], 1),
            "icon": interpret_weather_code(data["weather_code"][i])[0],
            "condition": interpret_weather_code(data["weather_code"][i])[1],
        })
    return weather_days


def weather_ip_view(request):
    error = None
    weather_data = []
    city = "Неизвестно"
    recommendations = None

    geo = getattr(request, 'client_ip', None)

    if geo and geo.get('status') == 'success':
        lat = geo.get('lat')
        lon = geo.get('lon')
        city = f"{geo.get('city')}, {geo.get('country')}"

        try:
            weather_data = fetch_opemeteo_forecast(lat, lon)

            # === ВАЖНО: ВЫЗОВ LLM ===
            print("🔄 Запуск LLM-рекомендаций...")   # ← должен появиться
            user_profile = {
                'age': getattr(request.user, 'age', 35),
                'height': getattr(request.user, 'height', 175),
                'weight': getattr(request.user, 'weight', 75),
                'sensitivity': request.GET.get('sensitivity', 'medium'),
                'is_sick': getattr(request.user, 'is_sick', False),
            }
            recommendations = get_biometeo_recommendations(weather_data, user_profile)

        except Exception as e:
            error = f"Ошибка: {str(e)}"
            print("Ошибка в weather_ip_view:", e)
    else:
        error = "Не удалось определить местоположение по IP."

    context = {
        'city': city,
        'weather_data_json': json.dumps(weather_data, ensure_ascii=False),
        'recommendations_json': json.dumps(recommendations, ensure_ascii=False) if recommendations else 'null',
        'error': error,
    }
    return render(request, 'weather.html', context)