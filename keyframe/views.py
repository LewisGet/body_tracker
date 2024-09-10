from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views import View

from django.db.models import Avg
from django.utils import timezone
from datetime import timedelta

from record.models import ActionLog
from .models import Keyframe
from .forms import *
import json


class KeyframeListView(ListView):
    model = Keyframe
    template_name = 'keyframe_list.html'

class KeyframeCreateView(CreateView):
    model = Keyframe
    form_class = KeyframeForm
    template_name = 'base_form.html'
    success_url = '/keyframes/'

class KeyframeUpdateView(UpdateView):
    model = Keyframe
    form_class = KeyframeForm
    template_name = 'base_form.html'
    success_url = '/keyframes/'

class KeyframeDeleteView(DeleteView):
    model = Keyframe
    template_name = 'keyframe_confirm_delete.html'
    success_url = '/keyframes/'


class BatchKeyframeCreateView(View):
    def get(self, request):
        form = BatchKeyframeForm()
        return render(request, 'batch_keyframe_form.html', {'form': form})

    def post(self, request):
        form = BatchKeyframeForm(request.POST)
        if form.is_valid():
            timestamps = form.cleaned_data['timestamps']
            for image_log in timestamps:
                Keyframe.objects.create(
                    timestamp=image_log.timestamp,
                    description=''
                )
            return redirect('keyframe_list')
        return render(request, 'keyframe/batch_keyframe_form.html', {'form': form})


class SmoothFrameView(View):
    def get(self, request):
        time_range = int(request.GET.get('time_range', 100))  # 毫秒
        split_range  = float(request.GET.get('split_range', 0.01))  # 百分比
        split_parts = request.GET.get('split_parts', '0.25,0.5,0.75')
        split_parts = [float(point) for point in split_parts.split(',')]

        finger_keyframe_logs = []
        body_keyframe_logs = []
        finger_segment_logs = []
        body_segment_logs = []

        all_keyframes = Keyframe.objects.all().order_by('timestamp')
        all_finger_logs = ActionLog.objects.filter(finger__isnull=False)
        all_body_logs = ActionLog.objects.filter(head_arm_leg_body__isnull=False)

        for keyframe in all_keyframes:
            finger_keyframe_logs.extend(self.avg_logs(keyframe.timestamp, time_range, all_finger_logs))
            body_keyframe_logs.extend(self.avg_logs(keyframe.timestamp, time_range, all_body_logs))


        if len(finger_keyframe_logs) == 0:
            return JsonResponse({'error': "finger action must be present near keyframe timestamp."}, status=404)

        if len(body_keyframe_logs) == 0:
            return JsonResponse({'error': "body action must be present near keyframe timestamp."}, status=404)

        for i in range(len(all_keyframes) - 1):
            start_time = all_keyframes[i].timestamp
            end_time = all_keyframes[i + 1].timestamp
            total_gap = (end_time - start_time).total_seconds() * 1000

            for split in split_parts:
                base_split_time = start_time + timedelta(milliseconds=total_gap * split)

                finger_segment_logs.extend(self.avg_logs(base_split_time, total_gap * split_range, all_finger_logs))
                body_segment_logs.extend(self.avg_logs(base_split_time, total_gap * split_range, all_body_logs))

        context = {
            'finger_keyframe_logs': finger_keyframe_logs,
            'body_keyframe_logs': body_keyframe_logs,
            'finger_segment_logs': finger_segment_logs,
            'body_segment_logs': body_segment_logs,
        }

        return JsonResponse(context, status=201)

    def avg_logs(self, base_timestamp, time_window, logs):
        filtered_logs = []

        start_time = base_timestamp - timedelta(milliseconds=time_window)
        end_time = base_timestamp + timedelta(milliseconds=time_window)
        logs = logs.filter(timestamp__range=(start_time, end_time))

        if logs.exists():
            avg_x = logs.aggregate(Avg('x'))['x__avg']
            avg_y = logs.aggregate(Avg('y'))['y__avg']
            avg_z = logs.aggregate(Avg('z'))['z__avg']

            filtered_logs.append({
                'timestamp': base_timestamp,
                'x': avg_x,
                'y': avg_y,
                'z': avg_z,
                's': start_time,
                'e': end_time
            })

        return filtered_logs
