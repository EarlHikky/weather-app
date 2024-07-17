from urllib.parse import quote, unquote

from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from httpx import ConnectError, HTTPStatusError
from rest_framework.filters import OrderingFilter
from rest_framework.generics import ListAPIView

from .models import SearchHistory
from .serializers import SearchHistorySerializer
from .utils import save_search_history, fetch_weather_data, get_context, validate_city, httpx_get, get_geo_location


class SearchHistoryAPIView(ListAPIView):
    queryset = SearchHistory.objects.all()
    serializer_class = SearchHistorySerializer
    filter_backends = [OrderingFilter]
    ordering_fields = ['search_count', 'city']
    ordering = ['-search_count']


def render_weather_response(request: WSGIRequest, context: dict) -> HttpResponse:
    return render(request, 'weather/index.html', context)


def get_weather(request: WSGIRequest) -> HttpResponse:
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
        if validate_city(query):
            results = get_geo_location(query, 5)
            if results:
                cities = [result['display_name'] for result in results]
                return JsonResponse(cities, safe=False)
    return JsonResponse([], safe=False)
