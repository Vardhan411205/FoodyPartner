#!/bin/bash

echo "Starting build process..."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Install or upgrade pip
echo "Upgrading pip..."
python -m pip install --upgrade pip

# Install requirements
echo "Installing requirements..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo "Warning: requirements.txt not found"
fi

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Run migrations
echo "Running database migrations..."
python manage.py makemigrations
python manage.py migrate

# Clear Python cache files
echo "Cleaning up cache files..."
find . -type d -name "__pycache__" -exec rm -r {} +
find . -type f -name "*.pyc" -delete

# Run tests if they exist
echo "Running tests..."
python manage.py test

# Check for deployment environment
if [ "$DJANGO_SETTINGS_MODULE" = "production" ]; then
    echo "Deploying to production..."
    # Add production-specific commands here
    
    # Restart Gunicorn if it's being used
    if command -v gunicorn &> /dev/null; then
        echo "Restarting Gunicorn..."
        sudo systemctl restart gunicorn
    fi
    
    # Restart Nginx if it's being used
    if command -v nginx &> /dev/null; then
        echo "Restarting Nginx..."
        sudo systemctl restart nginx
    fi
else
    echo "Starting development server..."
    python manage.py runserver
fi

echo "Build process completed!"
