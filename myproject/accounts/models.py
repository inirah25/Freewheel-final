from django.db import models
from django.utils import timezone

STATUS_CHOICES = [
    ('logged in', 'Logged In'),
    ('logged off', 'Logged Off'),
    ('busy', 'Busy'),
    ('brb', 'BRB'),
    ('lunch', 'Lunch'),
    ('meeting', 'Meeting'),
]

ACCESS_CHOICES = [
    ('admin', 'Admin'),
    ('staff', 'Staff'),
    ('guest', 'Guest'),
]



REPORTING_MANAGER_CHOICES = [
    ('aravindh_sarvalingham', 'Aravindh Sarvalingham'),
    ('sornambigai', 'Sornambigai'),
]

class Notice(models.Model):
    message = models.TextField()
    posted_by = models.CharField(max_length=100)
    posted_at = models.DateTimeField(auto_now_add=True)
 
    def __str__(self):
        return f"{self.posted_by} at {self.posted_at}"
 

class User(models.Model):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    password = models.CharField(max_length=128)
    role = models.CharField(max_length=50)  # Manager / Trayaj / Captain / Employee

    access = models.CharField(max_length=10, choices=ACCESS_CHOICES, default='guest')  # Replaces is_admin

    shift = models.CharField(max_length=10, blank=True, null=True)  # S1, S2, etc.
    reporting_manager = models.CharField(
    max_length=100,
    choices=REPORTING_MANAGER_CHOICES,
    blank=True,
    null=True
)

    employee_id = models.CharField(max_length=20, blank=True, null=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='logged off')

    reset_token = models.CharField(max_length=64, blank=True, null=True)
    token_created_at = models.DateTimeField(blank=True, null=True)

    teams_chat_link = models.URLField(max_length=255, blank=True, null=True)
    profile_image = models.ImageField(upload_to='profile_images/', default='profile_images/sample.png', blank=True, null=True)

    def __str__(self):
        return self.username

    def token_is_valid(self):
        if self.token_created_at is None:
            return False
        return timezone.now() - self.token_created_at < timezone.timedelta(hours=1)
