from django.urls import path
from .views import *


urlpatterns = [
    path('api/finger/', FingerView.as_view(), name='finger'),
    path('api/update_baseline/', UpdateBaselineView.as_view(), name='update_baseline'),
    path('api/action_log/', ActionLogView.as_view(), name='action_log'),
]
