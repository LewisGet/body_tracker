from django.contrib import admin
from .models import *


@admin.register(Keyframe)
class KeyframeAdmin(admin.ModelAdmin):
    list_display = ('id', 'timestamp')
