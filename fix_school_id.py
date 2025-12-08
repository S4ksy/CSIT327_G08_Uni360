import os
import sys
import django

# Add current directory to Python path
sys.path.insert(0, os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.core.settings')
django.setup()

from core.pos.models import Profile

# Set school_id to username for profiles where it's None or empty
for profile in Profile.objects.filter(school_id__isnull=True) | Profile.objects.filter(school_id=''):
    profile.school_id = profile.user.username
    profile.save()
    print(f"Set school_id for user {profile.user.username} to {profile.school_id}")

print("Done")
