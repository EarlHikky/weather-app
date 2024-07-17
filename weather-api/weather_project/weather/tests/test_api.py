from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from weather.models import SearchHistory
from weather.serializers import SearchHistorySerializer


class SearchHistoryAPITest(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.url = reverse('search_history_list')
        city_1 = SearchHistory.objects.create(city='New York', search_count=5)
        city_2 = SearchHistory.objects.create(city='Los Angeles', search_count=3)
        self.serializer_data = SearchHistorySerializer([city_1, city_2], many=True).data

    def test_list_search_history(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, self.serializer_data)

    def test_ordering_search_history_city_asc(self):
        response = self.client.get(self.url, {'ordering': 'city'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['city'], 'Los Angeles')
        self.assertEqual(response.data[1]['city'], 'New York')

    def test_ordering_search_history_city_desc(self):
        response = self.client.get(self.url, {'ordering': '-city'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['city'], 'New York')
        self.assertEqual(response.data[1]['city'], 'Los Angeles')

    def test_ordering_search_history_search_count_asc(self):
        response = self.client.get(self.url, {'ordering': 'search_count'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['city'], 'Los Angeles')
        self.assertEqual(response.data[1]['city'], 'New York')

    def test_ordering_search_history_search_count_desc(self):
        response = self.client.get(self.url, {'ordering': '-search_count'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['city'], 'New York')
        self.assertEqual(response.data[1]['city'], 'Los Angeles')
