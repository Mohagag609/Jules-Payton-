#!/bin/bash

# Install Python dependencies using pip with break-system-packages flag
echo "Installing Python dependencies..."
pip install --break-system-packages -r accounting_app/requirements.txt

# Build CSS
echo "Building CSS..."
cd /workspace
npm run build-css

# Run Django migrations
echo "Running migrations..."
cd accounting_app
python3 manage.py migrate

# Create a superuser if it doesn't exist
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@example.com', 'admin123')" | python3 manage.py shell

# Collect static files
echo "Collecting static files..."
python3 manage.py collectstatic --noinput

# Run the development server
echo "Starting development server..."
python3 manage.py runserver 0.0.0.0:8000