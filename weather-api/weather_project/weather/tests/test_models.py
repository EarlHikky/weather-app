from weather.models import SearchHistory
from django.test import TestCase


class SearchHistoryModelTest(TestCase):

    def setUp(self):
        SearchHistory.objects.create(city='New York', search_count=5)
        SearchHistory.objects.create(city='Los Angeles', search_count=3)

    def test_city_field(self):
        city_1 = SearchHistory.objects.get(city='New York')
        city_2 = SearchHistory.objects.get(city='Los Angeles')
        self.assertEqual(city_1.city, 'New York')
        self.assertEqual(city_2.city, 'Los Angeles')

    def test_search_count_field(self):
        city_1 = SearchHistory.objects.get(city='New York')
        city_2 = SearchHistory.objects.get(city='Los Angeles')
        self.assertEqual(city_1.search_count, 5)
        self.assertEqual(city_2.search_count, 3)

    def test_default_search_count(self):
        city_3 = SearchHistory.objects.create(city='San Francisco')
        self.assertEqual(city_3.search_count, 0)

    def test_str_method(self):
        city_1 = SearchHistory.objects.get(city='New York')
        self.assertEqual(str(city_1), 'New York - 5')

    def test_update_search_count(self):
        city_1 = SearchHistory.objects.get(city='New York')
        city_1.search_count += 10
        city_1.save()
        self.assertEqual(city_1.search_count, 15)
