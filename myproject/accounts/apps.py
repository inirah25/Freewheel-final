from django.apps import AppConfig
 
 
class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'
 
    def ready(self):
        from . import email_scheduler
        email_scheduler.start_scheduler_once()