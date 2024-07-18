from json import loads
from re import match as re_match

from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch


class GetWeatherViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.url = reverse('get_weather')

    @patch('weather.views.fetch_weather_data')
    @patch('weather.views.save_search_history')
    def test_get_weather_post_valid_city(self, mock_save_search_history, mock_fetch_weather_data):
        mock_weather_data = {
            'hourly': {
                'time': ['2024-07-17T00:00', '2024-07-17T01:00', '2024-07-17T02:00'],
                'temperature_2m': [19.8, 20.0, 21.5]
            },
            'current': {
                'temperature_2m': 22.5
            }
        }
        mock_fetch_weather_data.return_value = ('New York', mock_weather_data, False)

        response = self.client.post(self.url, {'city': 'New York'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('weather/index.html', [t.name for t in response.templates])
        self.assertContains(response, 'New York')
        self.assertContains(response, '2024-07-17')
        self.assertContains(response, '22')
        mock_save_search_history.assert_called_once_with('New York')

    def test_get_weather_post_invalid_city(self):
        response = self.client.post(self.url, {'city': '42'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('weather/index.html', [t.name for t in response.templates])
        self.assertContains(response, 'Enter a valid city name')

    def test_get_weather_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('weather/index.html', [t.name for t in response.templates])

    @patch('weather.views.fetch_weather_data')
    def test_get_weather_post_server_error(self, mock_fetch_weather_data):
        mock_fetch_weather_data.return_value = ('', {}, True)
        response = self.client.post(self.url, {'city': 'New York'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Try a few moments later')

    @patch('weather.views.fetch_weather_data')
    def test_get_weather_post_data_none(self, mock_fetch_weather_data):
        mock_fetch_weather_data.return_value = ('', None, False)
        response = self.client.post(self.url, {'city': 'New York'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'New York')


class AutocompleteCityViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.url = reverse('autocomplete_city')

    def test_autocomplete_city(self):
        response = self.client.get(self.url, {'term': 'Washington'})
        self.assertEqual(response.status_code, 200)
        parsed_list = loads(response.content.decode('utf-8'))
        for city in parsed_list:
            match = re_match(r'\bWashington\b', city)
            if match:
                break
        else:
            self.fail('Washington not found')

    def test_autocomplete_city_missing_term(self):
        response = self.client.get(self.url, {})
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, [])

    def test_autocomplete_city_invalid_term(self):
        response = self.client.get(self.url, {'term': '42#%@#'})
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, [])
