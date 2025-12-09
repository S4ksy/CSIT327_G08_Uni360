from django.core.management.base import BaseCommand
from ...models import Profile
import re

class Command(BaseCommand):
    help = 'Clean full_name fields by removing newlines and extra spaces'

    def handle(self, *args, **options):
        profiles = Profile.objects.exclude(full_name__isnull=True).exclude(full_name='')
        self.stdout.write(f'Processing {profiles.count()} profiles')
        for profile in profiles:
            original = profile.full_name
            cleaned = re.sub(r'\s+', ' ', original).strip()
            if cleaned != original:
                profile.full_name = cleaned
                profile.save()
                self.stdout.write(f'Cleaned full_name for user {profile.user.username}: "{original}" -> "{cleaned}"')
        self.stdout.write('Done')