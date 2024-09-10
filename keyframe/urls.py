from django.urls import path
from .views import *


urlpatterns = [
    path('', KeyframeListView.as_view(), name='keyframe_list'),
    path('new/', KeyframeCreateView.as_view(), name='keyframe_create'),
    path('<int:pk>/edit/', KeyframeUpdateView.as_view(), name='keyframe_edit'),
    path('<int:pk>/delete/', KeyframeDeleteView.as_view(), name='keyframe_delete'),
    path('batch/create/', BatchKeyframeCreateView.as_view(), name='keyframe_batch_create'),
]
