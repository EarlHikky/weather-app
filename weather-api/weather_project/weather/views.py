from django.shortcuts import render
from django.http import JsonResponse
import requests


def get_weather(request):
    weather_data = None
    if request.method == 'POST':
        city = request.POST.get('city')
        weather_data = fetch_weather_data(city)
    return render(request, 'weather/index.html', {'weather_data': weather_data})


def fetch_weather_data(city):
    geocode_url = f'https://nominatim.openstreetmap.org/search?q={city}&format=json&limit=1'
    geocode_response = requests.get(geocode_url)
    if geocode_response.status_code == 200 and geocode_response.json():
        location = geocode_response.json()[0]
        latitude = location['lat']
        longitude = location['lon']

        weather_url = f'https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current_weather=true'
        weather_response = requests.get(weather_url)
        if weather_response.status_code == 200:
            data = weather_response.json()
            return {
                'city': city,
                'temperature': data['current_weather']['temperature'],
                'wind_speed': data['current_weather']['windspeed'],
                'description': data['current_weather']['weathercode']
            }
    return None