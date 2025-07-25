#!/bin/sh
set -e

echo "Running migrations..."
python manage.py migrate

# Only run cities_light if there are no cities in the database
if [ "$(python manage.py shell -c 'from cities_light.models import City; print(City.objects.count())')" = "0" ]; then
  echo "Loading cities_light data..."
  python manage.py cities_light
else
  echo "cities_light data already loaded. Skipping."
fi

echo "Starting app..."
exec "$@"
