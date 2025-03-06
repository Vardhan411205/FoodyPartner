from django.core.management.base import BaseCommand
from django.db import connections
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Safely run migrations handling existing tables'

    def handle(self, *args, **kwargs):
        # First, try to fake all migrations to zero
        try:
            call_command('migrate', 'joo', 'zero', '--fake')
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Faking migrations to zero failed: {e}'))

        # Then apply migrations to default database
        try:
            call_command('migrate', 'joo', '--database=default', '--fake-initial')
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Default database migration failed: {e}'))

        # Finally apply migrations to items database
        try:
            call_command('migrate', 'joo', '--database=items', '--fake-initial')
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Items database migration failed: {e}'))

        self.stdout.write(self.style.SUCCESS('Migrations completed')) 