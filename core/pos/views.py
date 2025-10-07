from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
import re


def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('student_email')
        password = request.POST.get('password')
        from django.contrib.auth.models import User
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

def logout_view(request):
    logout(request)
    return redirect('login')
