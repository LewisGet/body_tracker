from django.urls import path
from .views import *


urlpatterns = [
    path('api/finger/', FingerView.as_view(), name='finger'),
    path('api/update_baseline/', UpdateBaselineView.as_view(), name='update_baseline'),
    path('api/create/action_log/', CreateActionLogView.as_view(), name='create_action_log'),
    path('image_log/create', CreateImageLogView.as_view(), name='create_image_log'),
    path('reset_log', ResetLogView.as_view(), name='reset_log'),
]
