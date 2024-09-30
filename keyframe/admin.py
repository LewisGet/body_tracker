from django.contrib import admin
from body_tracker.common_admin import BaseAdmin
from .models import *


@admin.register(Keyframe)
class KeyframeAdmin(BaseAdmin):
    list_display = ('id', 'formatted_datetime')
