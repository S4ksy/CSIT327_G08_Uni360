from django.urls import path
from . import views

urlpatterns = [
    # Auth routes
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('logout/', views.logout_view, name='logout'),

    # Public pages
    path('home/', views.home_view, name='home'),
    path('features/', views.features_view, name='features'),
    path('about/', views.about_view, name='about'),

    # Campus Navigation
    path('map/', views.map_view, name='map'),

    # Safety Alerts
    path('send-alert/', views.send_alert_view, name='send_alert'),
    path('get-alerts/', views.get_alerts_view, name='get_alerts'),
    path('get-unread-alerts/', views.get_unread_alerts_count, name='get_unread_alerts'),
    path('safety/', views.safety_view, name='safety'),
    path('notifications/', views.notifications_view, name='notifications'),
]
