from django.urls import path
from .views import *


urlpatterns = [
    path('api/finger/', FingerView.as_view(), name='finger'),
    path('api/action_log/', ActionLogView.as_view(), name='action_log'),
]
