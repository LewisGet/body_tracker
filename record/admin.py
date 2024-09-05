from django.contrib import admin
from .models import Finger, ActionLog


@admin.register(Finger)
class FingerAdmin(admin.ModelAdmin):
    list_display = ('hand', 'finger_index', 'segment_type', 'baseline_x', 'baseline_y', 'baseline_z')
    list_filter = ('hand', 'finger_index', 'segment_type')
    search_fields = ('hand', 'finger_index', 'segment_type')


@admin.register(ActionLog)
class ActionLogAdmin(admin.ModelAdmin):
    list_display = ('finger', 'x', 'y', 'z', 'timestamp')
    search_fields = ('finger__hand', 'finger__finger_index')
