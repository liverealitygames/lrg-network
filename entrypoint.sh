#!/bin/sh
set -e

echo "Running migrations..."
python manage.py migrate

# Only run cities_light if there are no cities in the database
CITY_COUNT=$(python manage.py shell -c 'from cities_light.models import City; print(City.objects.count())' | tail -n 1)

if [ "$CITY_COUNT" = "0" ]; then
  echo "Loading cities_light data..."
  python manage.py cities_light
else
  echo "cities_light has $CITY_COUNT cities. Skipping."
fi

echo "Starting app..."
exec "$@"
