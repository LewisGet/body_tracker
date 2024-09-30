from django.urls import path
from django.views.generic import TemplateView
from .views import *


urlpatterns = [
    path('api/finger/', FingerView.as_view(), name='finger'),
    path('api/update_baseline/', UpdateBaselineView.as_view(), name='update_baseline'),
    path('api/create/action_log/', CreateActionLogView.as_view(), name='create_action_log'),
    path('api/batch/create/action_log/', BatchCreateActionLogView.as_view(), name='batch_create_action_log'),
    path('image_log/create', CreateImageLogView.as_view(), name='create_image_log'),
    path('reset_log', ResetLogView.as_view(), name='reset_log'),
    path('api/onoff', ToggleApiView.as_view(), name='api_on_off'),
    path('panel', TemplateView.as_view(template_name='panel.html'), name='panel'),
    path('api/scan/location', ScanLocationView.as_view(), name='api_scan_location'),
    path('hardware/connect/status', HardwareStatusView.as_view(), name='hardware_status_view'),
    path('setup/baseline/', SetupBaselineView.as_view(), name='setup_baseline'),
]
