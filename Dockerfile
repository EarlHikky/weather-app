FROM python:3.11.4-alpine3.18

COPY requirements.txt /temp/requirements.txt
RUN pip install --no-cache-dir -r /temp/requirements.txt

WORKDIR /srv/www/weather-app

COPY weather_project /srv/www/weather-app

RUN python manage.py migrate

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
