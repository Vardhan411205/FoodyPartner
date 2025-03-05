#!/usr/bin/env bash
# exit on error
set -o errexit

# Install python dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput

# Run migrations for both databases
echo "Making migrations..."
python manage.py makemigrations joo

echo "Applying migrations to default database..."
python manage.py migrate --database=default

echo "Creating database schema..."
python manage.py dbshell --database=items << EOF
CREATE SCHEMA IF NOT EXISTS public;
GRANT ALL ON SCHEMA public TO public;
EOF

echo "Applying migrations to items database..."
python manage.py migrate --database=items
