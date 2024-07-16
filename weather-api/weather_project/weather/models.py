from django.db import models


class WeatherData(models.Model):
    city = models.CharField(max_length=100)
    temperature = models.FloatField()
    wind_speed = models.FloatField()
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.city} - {self.temperature}°C'


# weather/models.py


class SearchHistory(models.Model):
    city = models.CharField(max_length=100)
    search_count = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.city} - {self.search_count}'
