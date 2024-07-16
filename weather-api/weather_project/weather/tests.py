from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch
from weather.views import fetch_weather_data

class WeatherViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.url = reverse('get_weather')

    def test_get_weather_view_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'weather/index.html')

    @patch('weather.views.fetch_weather_data')
    def test_get_weather_view_post(self, mock_fetch_weather_data):
        mock_fetch_weather_data.return_value = {
            'city': 'Berlin',
            'temperature': 20,
            'wind_speed': 5,
            'description': 'Clear sky'
        }
        response = self.client.post(self.url, {'city': 'Berlin'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'weather/index.html')
        self.assertContains(response, 'Weather in Berlin')
        self.assertContains(response, 'Temperature: 20°C')
        self.assertContains(response, 'Wind Speed: 5 m/s')
        self.assertContains(response, 'Condition: Clear sky')


class FetchWeatherDataTests(TestCase):

    @patch('weather.views.requests.get')
    def test_fetch_weather_data_success(self, mock_get):
        mock_get.side_effect = [
            MockResponse({
                'lat': '52.5200',
                'lon': '13.4050'
            }, 200),
            MockResponse({
                'current_weather': {
                    'temperature': 20,
                    'windspeed': 5,
                    'weathercode': 'Clear sky'
                }
            }, 200)
        ]
        data = fetch_weather_data('Berlin')
        self.assertIsNotNone(data)
        self.assertEqual(data['city'], 'Berlin')
        self.assertEqual(data['temperature'], 20)
        self.assertEqual(data['wind_speed'], 5)
        self.assertEqual(data['description'], 'Clear sky')

    @patch('weather.views.requests.get')
    def test_fetch_weather_data_failure(self, mock_get):
        mock_get.return_value = MockResponse({}, 404)
        data = fetch_weather_data('InvalidCity')
        self.assertIsNone(data)


class MockResponse:
    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data
