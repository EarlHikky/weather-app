from datetime import datetime
from string import punctuation

from httpx import get as httpx_get

from .models import SearchHistory
import json
import os


def save_search_history(city: str) -> None:
    search_history, _ = SearchHistory.objects.get_or_create(city=city)
    search_history.search_count += 1
    search_history.save()


def fetch_weather_data(city: str) -> tuple[str | None, dict | None, bool | None]:
    with open(f'/home/earl/PycharmProjects/weather-api/weather_project/weather{city}.json', 'r', encoding='utf-8') as f: # TODO
        weather_data = json.load(f)
        return city, weather_data, None

    geocode_url = f'https://nominatim.openstreetmap.org/search?q={city}&format=json&limit=1'
    geocode_response = httpx_get(geocode_url)
    geo_status_code = geocode_response.status_code
    if geo_status_code == 403:
        return None, None, True

    geocode_response_data: dict = geocode_response.json()
    if geo_status_code == 200 and geocode_response_data:
        location: dict = geocode_response_data[0]
        lat: str = location['lat']
        lon: str = location['lon']
        city_name: str = location.get('name', city)

        weather_url = f'https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m&hourly=temperature_2m&timezone=auto&forecast_days=1'
        weather_response = httpx_get(weather_url)

        if weather_response.status_code == 200:
            weather_data: dict = weather_response.json()

            # Сохранение данных в файл  # TODO
            filename = f'weather{city_name}.json'
            filepath = os.path.join('./', filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(weather_data, f, ensure_ascii=False, indent=4)

            return city_name, weather_data, None

    return None, None, True


def get_context(weather_data: dict, request_city: str, city: str) -> dict:
    weather_data_times = weather_data['hourly']['time']
    weather_data_temperatures = weather_data['hourly']['temperature_2m']
    current_temperature = weather_data['current']['temperature_2m']
    context = {'weather_data_times': weather_data_times,
               'weather_data_temperatures': weather_data_temperatures,
               'last_city': request_city,
               'city': city,
               'current_date': datetime.now().strftime('%Y-%m-%d'),
               'current_temperature': current_temperature}
    return context


def validate_city(city: str) -> bool:
    if city.isdigit() or all(char in punctuation for char in city):
        return False
    return True
