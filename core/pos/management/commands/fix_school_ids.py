from django.core.management.base import BaseCommand
from ...models import Profile
import re

class Command(BaseCommand):
    help = 'Fix school_id for existing profiles by extracting from email'

    def handle(self, *args, **options):
        profiles = Profile.objects.filter(school_id__isnull=True) | Profile.objects.filter(school_id='')
        self.stdout.write(f'Processing {profiles.count()} profiles')
        for profile in profiles:
            # Set school_id to username
            profile.school_id = profile.user.username
            profile.save()
            self.stdout.write(f'Updated school_id for user {profile.user.username} to {profile.school_id}')
        self.stdout.write('Done')
