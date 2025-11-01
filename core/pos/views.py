from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from .models import Profile, Building, Alert
import re
import json

# -----------------------------
# AUTHENTICATION VIEWS
# -----------------------------

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('student_email')
        password = request.POST.get('password')
        try:
            user_obj = User.objects.get(email=email)
            user = authenticate(request, username=user_obj.username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
            else:
                return render(request, 'pos/login.html', {'error': 'Invalid email or password'})
        except User.DoesNotExist:
            return render(request, 'pos/login.html', {'error': 'No account found for this email'})
    return render(request, 'pos/login.html')


def signup_view(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        student_email = request.POST.get('student_email')
        student_id = request.POST.get('student_id')
        password = request.POST.get('password')

        error = None

        email_pattern = r'^[a-zA-Z]+(\.[a-zA-Z]+)+@cit\.edu$'
        student_id_pattern = r'^\d{2}-\d{4}-\d{3}$'

        if not re.match(email_pattern, student_email or ''):
            error = 'Invalid email format. Use firstname.lastname@cit.edu'
        elif not re.match(student_id_pattern, student_id or ''):
            error = 'Invalid Student ID format. Use 23-6555-528'
        elif not full_name or not password:
            error = 'All fields are required.'
        elif User.objects.filter(username=student_id).exists():
            error = 'This Student ID is already registered.'
        elif User.objects.filter(email=student_email).exists():
            error = 'This email is already registered.'

        if error:
            return render(request, 'pos/signup.html', {'error': error})

        # Create the user
        user = User.objects.create_user(username=full_name, email=student_email, password=password)
        user.save()

        return redirect('login')

    return render(request, 'pos/signup.html')


@login_required
def dashboard(request):
    return render(request, 'pos/dashboard.html')


@login_required
def profile_view(request):
    if request.method == 'POST':
        profile_picture = request.FILES.get('profile_picture')
        if profile_picture:
            profile, created = Profile.objects.get_or_create(user=request.user)
            profile.profile_picture = profile_picture
            profile.save()
            messages.success(request, 'Profile picture updated successfully!')
        return redirect('profile')
    return render(request, 'pos/profile.html')


def logout_view(request):
    logout(request)
    return redirect('home')


# -----------------------------
# PUBLIC PAGES
# -----------------------------

def home_view(request):
    return render(request, 'pos/home.html')

def features_view(request):
    return render(request, 'pos/features.html')

def about_view(request):
    return render(request, 'pos/about.html')


# -----------------------------
# CAMPUS NAVIGATION VIEWS
# -----------------------------

@login_required
def map_view(request):
    buildings = Building.objects.all()
    buildings_data = [
        {
            'name': building.name,
            'description': building.description,
            'latitude': building.latitude,
            'longitude': building.longitude,
        }
        for building in buildings
    ]
    return render(request, 'pos/map.html', {'buildings': json.dumps(buildings_data)})


# -----------------------------
# SAFETY ALERT VIEWS
# -----------------------------

@login_required
def send_alert_view(request):
    if request.method == 'POST':
        alert_type = request.POST.get('alert_type')
        location = request.POST.get('location', '')
        message = request.POST.get('message', '')

        Alert.objects.create(
            user=request.user,
            alert_type=alert_type,
            location=location,
            message=message
        )
        return JsonResponse({'status': 'success', 'message': 'Alert sent successfully!'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)
