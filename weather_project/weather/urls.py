from django.urls import path
from .views import get_weather, autocomplete_city, SearchHistoryAPIView

urlpatterns = [
    path('', get_weather, name='get_weather'),
    path('autocomplete/', autocomplete_city, name='autocomplete_city'),
    path('api/v1/search-list/', SearchHistoryAPIView.as_view(), name='search_history_list'),
]
