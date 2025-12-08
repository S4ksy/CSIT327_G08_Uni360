import os
import django
import sys

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.core.settings')
django.setup()

from django.contrib.auth.models import User
from core.pos.models import Profile

def create_missing_profiles():
    users_without_profiles = User.objects.filter(profile__isnull=True)
    print(f'Creating profiles for {users_without_profiles.count()} users...')

    for user in users_without_profiles:
        profile = Profile.objects.create(user=user)
        print(f'Created profile for {user.username}')

    print('Done.')

if __name__ == '__main__':
    create_missing_profiles()
