from django.db import models
from django.utils import timezone

class Admin(models.Model):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)  # Hashed password will be stored

    # Fields for password reset functionality
    reset_token = models.CharField(max_length=64, blank=True, null=True)
    token_created_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.username

    def token_is_valid(self):
        """Check if the reset token is not older than 1 hour."""
        if self.token_created_at is None:
            return False
        return timezone.now() - self.token_created_at < timezone.timedelta(hours=1)
