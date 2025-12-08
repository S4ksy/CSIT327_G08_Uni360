from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from core.pos.models import Alert

class Command(BaseCommand):
    help = 'Create a test alert for timestamp verification'

    def handle(self, *args, **options):
        try:
            user = User.objects.first()
            if user:
                alert = Alert.objects.create(
                    user=user,
                    alert_type='safety',
                    location='Test Location',
                    message='Test alert for timestamp verification'
                )
                # Convert to local timezone for display
                local_time = timezone.localtime(alert.timestamp)
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Test alert created successfully with ID: {alert.id}\n'
                        f'Created at (UTC): {alert.timestamp}\n'
                        f'Local time: {local_time}\n'
                        f'Formatted time: {local_time.strftime("%I:%M %p").lower()}'
                    )
                )
            else:
                self.stdout.write(
                    self.style.ERROR('No users found in database')
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating test alert: {e}')
            )
