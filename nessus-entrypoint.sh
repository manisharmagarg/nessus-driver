#!/bin/bash
echo "Make migrations..."

python manage.py db init

echo "Starting migrations..."

python manage.py db migrate

echo "upgrade migrations..."

python manage.py db upgrade

echo "Server started"

python manage.py runserver -h 0.0.0.0 -p 80 -d