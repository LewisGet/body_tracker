from django.urls import path
from .views import *


urlpatterns = [
    path('api/segment/', SegmentView.as_view(), name='segment'),
]
