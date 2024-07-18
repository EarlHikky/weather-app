from datetime import datetime
from logging import getLogger
from string import punctuation

from httpx import get as httpx_get, HTTPError

from .models import SearchHistory

logger = getLogger('django')


def save_search_history(city: str) -> None:
    search_history, _ = SearchHistory.objects.get_or_create(city=city)
    search_history.search_count += 1
    search_history.save()


def make_request(url: str) -> dict:
    try:
        response = httpx_get(url)
        response.raise_for_status()
        response_data = response.json()
        if response_data:
            return response_data
        return {}
    except HTTPError as e:
        logger.error(f'HTTP error occurred: {e}')
        return {}


def get_geo_location(query: str, limit: int = 1) -> dict:
    geocode_url = f'https://nominatim.openstreetmap.org/search?q={query}&format=json&limit={limit}'
    geocode_response_data = make_request(geocode_url)
    return geocode_response_data


def fetch_weather_data(city: str) -> tuple[str | None, dict | None, bool | None]:
    geocode_response_data: dict = get_geo_location(city)
    if not geocode_response_data:
        return None, None, True

    location: dict = geocode_response_data[0]
    lat: str = location['lat']
    lon: str = location['lon']
    city_name: str = location.get('name', city)

    weather_url = f'https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m&hourly=temperature_2m&timezone=auto&forecast_days=1'
    weather_data: dict = make_request(weather_url)
    if not weather_data:
        return None, None, False

    return city_name, weather_data, None


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
