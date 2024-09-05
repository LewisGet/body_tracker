from django.contrib import admin
from .models import Finger, Segment


@admin.register(Finger)
class FingerAdmin(admin.ModelAdmin):
    list_display = ('hand', 'finger_index')
    list_filter = ('hand', 'finger_index')
    search_fields = ('hand', 'finger_index')


@admin.register(Segment)
class SegmentAdmin(admin.ModelAdmin):
    list_display = ('finger', 'segment_type', 'x', 'y', 'z', 'timestamp')
    list_filter = ('finger', 'segment_type')
    search_fields = ('finger__hand', 'finger__finger_index', 'segment_type')
