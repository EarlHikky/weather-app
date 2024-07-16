from django.urls import path
from .views import get_weather, autocomplete_city, search_statistics

urlpatterns = [
    path('', get_weather, name='get_weather'),
    path('autocomplete/', autocomplete_city, name='autocomplete_city'),
    path('api/search_statistics/', search_statistics, name='search_statistics'),
]