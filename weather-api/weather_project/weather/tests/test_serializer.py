from unittest import TestCase

from weather.models import SearchHistory
from weather.serializers import SearchHistorySerializer


class SearchHistorySerializerTest(TestCase):
    def test_serializer(self):
        city_1 = SearchHistory.objects.create(city='New York', search_count=5)
        city_2 = SearchHistory.objects.create(city='Los Angeles', search_count=3)
        serializer_data = SearchHistorySerializer([city_1, city_2], many=True).data
        expected_data = [
            {
                'id': city_1.id,
                'city': 'New York',
                'search_count': 5
            },
            {
                'id': city_2.id,
                'city': 'Los Angeles',
                'search_count': 3
            }
        ]
        self.assertEqual(serializer_data, expected_data)

