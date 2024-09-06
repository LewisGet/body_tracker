from django.apps import AppConfig


class RecordConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'record'

    def ready(self):
        from .models import Finger, HeadArmLegBody

        try:
            Finger.initialize_fingers()
            HeadArmLegBody.initialize_parts()
        except:
            pass
