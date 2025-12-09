from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100, blank=True, null=True)  # Store full name
    school_id = models.CharField(max_length=20, blank=True, null=True)  # Store student ID
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    profile_picture_data = models.TextField(blank=True, null=True)  # Store base64 encoded image
    profile_picture_name = models.CharField(max_length=255, blank=True, null=True)  # Store original filename

    def save(self, *args, **kwargs):
        # Auto-fill full_name if empty
        if not self.full_name or self.full_name.strip() == "":
            full_name = f"{self.user.first_name} {self.user.last_name}".strip()
            if full_name:
                self.full_name = full_name
            else:
                self.full_name = self.user.username
        else:
            # Clean existing full_name
            import re
            self.full_name = re.sub(r'\s+', ' ', self.full_name).strip()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username}'s profile"

class Building(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return self.name

class Alert(models.Model):
    ALERT_TYPES = [
        ('emergency', 'Emergency'),
        ('safety', 'Safety Concern'),
        ('location_share', 'Location Share'),
        ('other', 'Other'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='received_alerts')
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES, default='other')
    location = models.CharField(max_length=255, blank=True)
    message = models.TextField(blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    read_by = models.ManyToManyField(User, related_name='read_alerts', blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.alert_type} at {self.timestamp}"


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        instance.profile.save()
