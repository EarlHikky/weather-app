from urllib.parse import quote, unquote

from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from rest_framework.generics import ListAPIView

from .models import SearchHistory
from .serializers import SearchHistorySerializer
from .utils import save_search_history, fetch_weather_data, get_context, validate_city, httpx_get


class SearchHistoryAPIView(ListAPIView):
    queryset = SearchHistory.objects.all()
    serializer_class = SearchHistorySerializer


def render_weather_response(request: WSGIRequest, context: dict) -> HttpResponse:
    return render(request, 'weather/index.html', context)


def get_weather(request: WSGIRequest) -> HttpResponse:
    weather_data = None
    last_city = request.COOKIES.get('last_city', '')

    if request.method == 'POST':
        request_city = request.POST.get('city')

        if not validate_city(request_city):
            return render_weather_response(request, {'last_city': 'Enter a valid city name'})

        city, weather_data, status_code = fetch_weather_data(request_city)

        if status_code:
            return render_weather_response(request, {'last_city': 'Try a few moments later'})

        if weather_data is None:
            return render_weather_response(request, {'last_city': request_city})

        save_search_history(city)
        context = get_context(weather_data, request_city, city)
        response = render_weather_response(request, context)
        response.set_cookie('last_city', quote(request_city))
        return response

    context = {'last_city': unquote(last_city)}
    return render_weather_response(request, context)


def autocomplete_city(request: WSGIRequest) -> JsonResponse:
    if 'term' in request.GET:
        query = request.GET.get('term')
        geocode_url = f'https://nominatim.openstreetmap.org/search?q={query}&format=json&limit=5'
        geocode_response = httpx_get(geocode_url)
        if geocode_response.status_code == 200:
            results = geocode_response.json()
            cities = [result['display_name'] for result in results]
            return JsonResponse(cities, safe=False)
    return JsonResponse([], safe=False)
