#!/usr/bin/env bash
# Build script for Render deployment

set -o errexit

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Create admin user if none exists
python manage.py create_admin

echo "Build completed successfully!"