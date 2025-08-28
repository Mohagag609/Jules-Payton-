#!/bin/bash

echo "Restarting the server with fixes..."

# Install Python dependencies
echo "Installing dependencies..."
cd /workspace/accounting_app
pip install --break-system-packages -r requirements.txt

# Collect static files
echo "Collecting static files..."
python3 manage.py collectstatic --noinput

echo "Server restart completed. The changes should now be visible."
echo "Please refresh your browser to see the updates."