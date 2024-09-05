from django.urls import path
from .views import *


urlpatterns = [
    path('api/finger/', FingerView.as_view(), name='finger'),
    path('api/segment/', SegmentView.as_view(), name='segment'),
]
