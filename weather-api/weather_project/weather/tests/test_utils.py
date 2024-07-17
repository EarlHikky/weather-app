from datetime import datetime

from django.test import TestCase

from weather.models import SearchHistory
from weather.utils import save_search_history, fetch_weather_data, get_context, validate_city, make_request, \
    get_geo_location


class UtilsTest(TestCase):

    def setUp(self):
        self.city_1 = 'New York'
        self.city_2 = 'Washington'
        self.city_3 = '42'
        self.city_4 = '$%#$'

    def test_make_request(self):
        response = make_request(f'https://nominatim.openstreetmap.org/search?q={self.city_2}&format=json&limit=1')
        self.assertIsInstance(response[0], dict)

    def test_get_geo_location(self):
        response = get_geo_location(self.city_2)
        self.assertIsInstance(response[0], dict)

    def test_save_search_history(self):
        save_search_history(self.city_1)
        save_search_history(self.city_2)
        save_search_history(self.city_2)
        search_history_1 = SearchHistory.objects.get(city=self.city_1)
        search_history_2 = SearchHistory.objects.get(city=self.city_2)
        self.assertEqual(search_history_1.search_count, 1)
        self.assertEqual(search_history_2.search_count, 2)

    def test_fetch_weather_data(self):
        city, weather_data, status_code = fetch_weather_data(self.city_1)
        try:
            self.assertIsNotNone(city)
        except AssertionError:
            print('ConnectError: Cannot connect to OpenWeatherMap API')
            city, weather_data, status_code = fetch_weather_data(self.city_1)
            self.assertIsNone(weather_data)
            self.assertIsNone(city)
            self.assertTrue(status_code)
        else:
            self.assertIn(self.city_1, city)
            self.assertIsNotNone(weather_data)
            self.assertIn('hourly', weather_data)
            self.assertIn('current', weather_data)
            self.assertEqual(status_code, None)

    def test_get_context(self):
        weather_data = {
            'hourly': {
                'time': ['2024-07-17T00:00', '2024-07-17T01:00', '2024-07-17T02:00'],
                'temperature_2m': [19.8, 20.0, 21.5]
            },
            'current': {
                'temperature_2m': 22.5
            }
        }
        request_city = 'New York'
        city = 'New York'
        expected_dict = {'weather_data_times': ['2024-07-17T00:00', '2024-07-17T01:00', '2024-07-17T02:00'],
                         'weather_data_temperatures': [19.8, 20.0, 21.5],
                         'last_city': request_city,
                         'city': city,
                         'current_date': datetime.now().strftime('%Y-%m-%d'),
                         'current_temperature': 22.5}
        context = get_context(weather_data, request_city, city)
        self.assertDictEqual(expected_dict, context)

    def test_validate_city(self):
        self.assertTrue(validate_city(self.city_1))
        self.assertTrue(validate_city(self.city_2))
        self.assertFalse(validate_city(self.city_3))
        self.assertFalse(validate_city(self.city_4))
