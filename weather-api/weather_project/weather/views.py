from re import match
from string import capwords, punctuation
from urllib.parse import quote, unquote

import requests
from django.shortcuts import render
from django.http import JsonResponse

from .models import SearchHistory


def get_weather(request):
    weather_data = None
    last_city = request.COOKIES.get('last_city', '')

    if request.method == 'POST':
        city = request.POST.get('city')

        if city.isdigit() or all(char in punctuation for char in city):
            return render(request,
                          'weather/index.html',
                          {'error': 'Invalid city name.',
                           'last_city': 'Enter a valid city name'}
                          )

        weather_data = fetch_weather_data(city)
        if not weather_data:
            return render(request,
                          'weather/index.html',
                          {'weather_data': weather_data,
                           'last_city': city}
                          )

        match_city = match(r'^[\w\s-]*\b', city)
        if match_city:
            city = capwords(match_city.group(0), sep='-')

        search_history, created = SearchHistory.objects.get_or_create(city=city)
        search_history.search_count += 1
        search_history.save()

        response = render(request,
                          'weather/index.html',
                          {'weather_data': weather_data,
                           'last_city': city}
                          )
        response.set_cookie('last_city', quote(city))
        return response

    return render(request,
                  'weather/index.html',
                  {'weather_data': weather_data,
                   'last_city': unquote(last_city)}
                  )


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


def autocomplete_city(request):
    if 'term' in request.GET:
        query = request.GET.get('term')
        geocode_url = f'https://nominatim.openstreetmap.org/search?q={query}&format=json&limit=5'
        geocode_response = requests.get(geocode_url)
        if geocode_response.status_code == 200:
            results = geocode_response.json()
            cities = [result['display_name'] for result in results]
            return JsonResponse(cities, safe=False)
    return JsonResponse([], safe=False)


def search_statistics(request):
    stats = SearchHistory.objects.all().values('city', 'search_count')
    return JsonResponse(list(stats), safe=False)
