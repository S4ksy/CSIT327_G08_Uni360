import os
import sys
import django

# Add current directory to Python path
sys.path.insert(0, os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.core.settings')
django.setup()

from core.pos.models import Profile

# Check school_id for all profiles
for profile in Profile.objects.all():
    print(f"User: {profile.user.username}, School ID: {profile.school_id}")

print("Done checking")
