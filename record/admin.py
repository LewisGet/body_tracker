from django.contrib import admin
from .models import *


@admin.register(Finger)
class FingerAdmin(admin.ModelAdmin):
    list_display = ('hand', 'finger_index', 'segment_type', 'baseline_x', 'baseline_y', 'baseline_z')
    list_filter = ('hand', 'finger_index', 'segment_type')
    search_fields = ('hand', 'finger_index', 'segment_type')


@admin.register(ActionLog)
class ActionLogAdmin(admin.ModelAdmin):
    list_display = ('finger', 'head_arm_leg_body', 'x', 'y', 'z', 'timestamp')
    search_fields = ('finger__hand', 'finger__finger_index', 'finger__segment_type', 'head_arm_leg_body__side', 'head_arm_leg_body__segment_type')


@admin.register(HeadArmLegBody)
class HeadArmLegBodyAdmin(admin.ModelAdmin):
    list_display = ('side', 'segment_type', 'baseline_x', 'baseline_y', 'baseline_z')
    list_filter = ('side', 'segment_type')
    search_fields = ('side', 'segment_type')
