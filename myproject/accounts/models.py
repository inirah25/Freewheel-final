from django.db import models
from django.utils import timezone
STATUS_CHOICES = [
    ('logged in', 'Logged In'),
    ('logged off', 'Logged off'),
    ('busy', 'Busy'),
    ('brb', 'BRB'),
    ('lunch', 'Lunch'),
    ('meeting', 'Meeting'),
]
 
status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
 
class Admin(models.Model):
    name = models.CharField(max_length=255, default='Admin User')
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)  # Hashed password will be stored
 
    # Fields for password reset functionality
    reset_token = models.CharField(max_length=64, blank=True, null=True)
    token_created_at = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
 
    def __str__(self):
        return self.username
 
    def token_is_valid(self):
        """Check if the reset token is not older than 1 hour."""
        if self.token_created_at is None:
            return False
        return timezone.now() - self.token_created_at < timezone.timedelta(hours=1)
 
 
from django.db import models
from django.utils import timezone
 
class Employee(models.Model):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    password = models.CharField(max_length=128)
    role = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
 
    # Add these two lines:
    reset_token = models.CharField(max_length=64, blank=True, null=True)
    token_created_at = models.DateTimeField(blank=True, null=True)
 
    def __str__(self):
        return self.username
 
    def token_is_valid(self):
        if self.token_created_at is None:
            return False
        return timezone.now() - self.token_created_at < timezone.timedelta(hours=1)
 
 
 
from django.db import models

class Notice(models.Model):
    message = models.TextField()
    posted_by = models.CharField(max_length=100)
    posted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.posted_by} at {self.posted_at}"