from django.apps import AppConfig

class AppInverMonitorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'AppInverMonitor'

    def ready(self):
        import AppInverMonitor.models