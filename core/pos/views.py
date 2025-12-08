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
        email = request.POST.get('student_email').lower()
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
        elif User.objects.filter(email__iexact=student_email).exists():
            error = 'This email is already registered.'

        if error:
            return render(request, 'pos/signup.html', {'error': error})

        # Create the user
        user = User.objects.create_user(username=student_id, email=student_email.lower(), password=password)
        user.save()

        # Save full_name and school_id to profile
        profile = user.profile
        profile.full_name = full_name
        profile.school_id = student_id
        profile.save()

        return redirect('login')

    return render(request, 'pos/signup.html')


@login_required
def dashboard(request):
    return render(request, 'pos/dashboard.html')


@login_required
def profile_view(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'update_picture':
            profile_picture = request.FILES.get('profile_picture')
            if profile_picture:
                profile, created = Profile.objects.get_or_create(user=request.user)

                # Read the file and encode as base64
                import base64
                from django.core.files.base import ContentFile

                # Read file content
                file_content = profile_picture.read()

                # Encode to base64
                encoded_image = base64.b64encode(file_content).decode('utf-8')

                # Store in database
                profile.profile_picture_data = f"data:{profile_picture.content_type};base64,{encoded_image}"
                profile.profile_picture_name = profile_picture.name
                profile.save()

                messages.success(request, 'Profile picture updated successfully!')
        elif action == 'update_school_id':
            student_id = request.POST.get('student_id')
            if student_id:
                import re
                student_id_pattern = r'^\d{2}-\d{4}-\d{3}$'
                if re.match(student_id_pattern, student_id):
                    profile, created = Profile.objects.get_or_create(user=request.user)
                    profile.school_id = student_id
                    profile.save()
                    # Check if request is AJAX
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': True, 'message': 'Student ID updated successfully!'})
                    messages.success(request, 'Student ID updated successfully!')
                else:
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'error': 'Invalid Student ID format. Use 23-6555-528'})
                    messages.error(request, 'Invalid Student ID format. Use 23-6555-528')
        elif action == 'change_password':
            current_password = request.POST.get('current_password')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')

            if not request.user.check_password(current_password):
                messages.error(request, 'Current password is incorrect.')
            elif new_password != confirm_password:
                messages.error(request, 'New passwords do not match.')
            elif len(new_password) < 8:
                messages.error(request, 'New password must be at least 8 characters long.')
            else:
                request.user.set_password(new_password)
                request.user.save()
                messages.success(request, 'Password changed successfully! Please log in again with your new password.')
                logout(request)
                return redirect('/login/')
        elif action == 'delete_profile':
            # Delete the user account
            request.user.delete()
            logout(request)
            messages.success(request, 'Your account has been deleted successfully.')
            return redirect('home')
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


@login_required
def safety_view(request):
    return render(request, 'pos/safety.html')


@login_required
def notifications_view(request):
    return render(request, 'pos/notifications.html')


@login_required
def get_alerts_view(request):
    # Get recent alerts (last 24 hours)
    from django.utils import timezone
    from datetime import timedelta

    recent_alerts = Alert.objects.filter(
        timestamp__gte=timezone.now() - timedelta(hours=24)
    ).exclude(
        alert_type='location_share',
        user=request.user
    ).order_by('-timestamp')[:10]  # Last 10 alerts, excluding location shares sent by current user

    alerts_data = [
        {
            'id': alert.id,
            'user': getattr(alert.user.profile, 'full_name', alert.user.username),
            'alert_type': alert.get_alert_type_display(),
            'location': alert.location,
            'message': alert.message,
            'timestamp': alert.timestamp.isoformat(),
            'formatted_time': timezone.localtime(alert.timestamp).strftime('%I:%M %p').lower(),
            'is_read': request.user in alert.read_by.all()
        }
        for alert in recent_alerts
    ]

    # Mark all as read for this user
    for alert in recent_alerts:
        alert.read_by.add(request.user)

    return JsonResponse({'alerts': alerts_data})


@login_required
def get_unread_alerts_count(request):
    from django.utils import timezone
    from datetime import timedelta

    unread_count = Alert.objects.filter(
        timestamp__gte=timezone.now() - timedelta(hours=24)
    ).exclude(read_by=request.user).count()

    return JsonResponse({'unread_count': unread_count})


@login_required
def get_users_view(request):
    users = User.objects.exclude(id=request.user.id).select_related('profile')
    users_data = [
        {
            'id': user.id,
            'username': user.username,
            'full_name': getattr(user.profile, 'full_name', user.username),
            'school_id': getattr(user.profile, 'school_id', ''),
        }
        for user in users
    ]
    return JsonResponse({'users': users_data})


@login_required
def share_location_view(request):
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        recipients = data.get('recipients', [])

        if not latitude or not longitude or not recipients:
            return JsonResponse({'status': 'error', 'message': 'Missing required data'}, status=400)

        try:
            # Create location share alerts for each recipient
            for recipient_id in recipients:
                recipient = User.objects.get(id=recipient_id)
                Alert.objects.create(
                    user=request.user,
                    alert_type='location_share',
                    location=f"{latitude},{longitude}",
                    message=f"{request.user.profile.full_name} shared their location with you"
                )

            return JsonResponse({'status': 'success', 'message': 'Location shared successfully'})
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'One or more recipients not found'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)


# -----------------------------
# CAMPUS NAVIGATION VIEWS
# -----------------------------

@login_required
def map_view(request):
    # Check if we have buildings in the database
    if Building.objects.exists():
        # Use buildings from database
        buildings = Building.objects.all()
        buildings_data = [
            {
                'name': building.name,
                'description': building.description,
                'latitude': float(building.latitude),
                'longitude': float(building.longitude),
                'color': getattr(building, 'color', '#6610F2'),
                'type': getattr(building, 'building_type', 'academic')
            }
            for building in buildings
        ]
    else:
        # Use hardcoded CIT-U buildings data
        buildings_data = [
            # Academic Buildings
            {
                "name": "ACAD Building",
                "description": "Main Academic Building",
                "latitude": 10.3232,
                "longitude": 123.9083,
                "color": "#6610F2",
                "type": "academic"
            },
            {
                "name": "NGE Building", 
                "description": "Engineering Building",
                "latitude": 10.3234,
                "longitude": 123.9086,
                "color": "#2EC4B6",
                "type": "academic"
            },
            {
                "name": "GLE Building",
                "description": "General Education Building", 
                "latitude": 10.3230,
                "longitude": 123.9081,
                "color": "#FF6B6B",
                "type": "academic"
            },
            {
                "name": "SAL Building",
                "description": "Science and Laboratory Building",
                "latitude": 10.3236, 
                "longitude": 123.9088,
                "color": "#FF9F1C",
                "type": "academic"
            },
            {
                "name": "ALLIED Building",
                "description": "Allied Health Sciences Building",
                "latitude": 10.3228,
                "longitude": 123.9079,
                "color": "#E71D36",
                "type": "academic"
            },
            {
                "name": "RTL Building",
                "description": "Research and Technology Laboratory",
                "latitude": 10.3231,
                "longitude": 123.9085,
                "color": "#4A90E2",
                "type": "academic"
            },
            
            # Library
            {
                "name": "College Library",
                "description": "Main Campus Library",
                "latitude": 10.3229,
                "longitude": 123.9082,
                "color": "#9C27B0",
                "type": "library"
            },
            
            # Sports Facilities
            {
                "name": "GYM",
                "description": "University Gymnasium",
                "latitude": 10.3225,
                "longitude": 123.9075,
                "color": "#FF5722",
                "type": "sports"
            },
            {
                "name": "Covered Court",
                "description": "Multi-purpose Covered Court",
                "latitude": 10.3223,
                "longitude": 123.9073,
                "color": "#795548",
                "type": "sports"
            },
            
            # Canteens
            {
                "name": "Main Canteen",
                "description": "Student Canteen and Food Court",
                "latitude": 10.3227,
                "longitude": 123.9077,
                "color": "#4CAF50",
                "type": "canteen"
            },
            {
                "name": "Annex Canteen",
                "description": "Secondary Student Canteen",
                "latitude": 10.3233,
                "longitude": 123.9084,
                "color": "#8BC34A",
                "type": "canteen"
            },
            
            # Parking Areas (5 total)
            {
                "name": "Main Parking",
                "description": "Student and Faculty Parking Area",
                "latitude": 10.3220,
                "longitude": 123.9070,
                "color": "#607D8B",
                "type": "parking"
            },
            {
                "name": "Annex Parking",
                "description": "Additional Parking Space",
                "latitude": 10.3235,
                "longitude": 123.9080,
                "color": "#78909C",
                "type": "parking"
            },
            {
                "name": "Gym Parking",
                "description": "Parking near Gymnasium",
                "latitude": 10.3222,
                "longitude": 123.9072,
                "color": "#90A4AE",
                "type": "parking"
            },
            {
                "name": "Library Parking",
                "description": "Parking near College Library",
                "latitude": 10.3226,
                "longitude": 123.9078,
                "color": "#B0BEC5",
                "type": "parking"
            },
            {
                "name": "Entrance Parking",
                "description": "Parking near Main Entrance",
                "latitude": 10.3219,
                "longitude": 123.9069,
                "color": "#CFD8DC",
                "type": "parking"
            },
            
            # Campus Entrance
            {
                "name": "N. Bacalso Entrance",
                "description": "Main Campus Entrance",
                "latitude": 10.3218,
                "longitude": 123.9068,
                "color": "#00BCD4",
                "type": "entrance"
            }
        ]
    
    return render(request, 'pos/map.html', {'buildings': json.dumps(buildings_data)})