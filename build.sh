#!/usr/bin/env bash

# Exit on error
set -o errexit

# Debugging information
echo "BUILD_ENV: $BUILD_ENV"
echo "PYTHON_VERSION: $PYTHON_VERSION"
echo "Working directory: $(pwd)"

# Python upgrade and setup
echo "Installing Python dependencies..."
python -m pip install --upgrade pip
pip install -r requirements.txt

# Django commands
echo "Running Django commands..."

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Run migrations for both databases
echo "Running database migrations..."
python manage.py makemigrations
python manage.py migrate
python manage.py migrate --database=default
python manage.py migrate --database=items

# Clean up cache
echo "Cleaning up cache files..."
find . -type d -name "__pycache__" -exec rm -r {} +
find . -type f -name "*.pyc" -delete

# Security check
echo "Running security checks..."
python manage.py check --deploy

# Verify static files
echo "Verifying static files..."
if [ -d "staticfiles" ]; then
    echo "Static files collected successfully"
else
    echo "Warning: staticfiles directory not found"
fi

# Production specific commands
if [ "$BUILD_ENV" = "production" ]; then
    echo "Running production setup..."
    
    # Compress static files
    if command -v gzip &> /dev/null; then
        find staticfiles -type f -regextype posix-extended -regex ".*\.(css|js|txt|html|xml)" -exec gzip -f -k {} \;
    fi
    
    # Set proper permissions
    chmod -R 755 staticfiles/
fi

echo "Build completed successfully!"
