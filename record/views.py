from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from .models import *
from .forms import *
import json


class GetPostView(View):
    def get(self, request):
        data = request.GET

        return self.create(data)

    def post(self, request):
        data = json.loads(request.body)

        return self.create(data)

    def create(self, data):
        return JsonResponse({'error': 'only extends.'}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class FingerView(View):
    def get(self, request):
        form = FingerForm(request.GET)

        if not form.is_valid():
            return JsonResponse({'error': 'Invalid input. Both hand and finger_index must be integers.'}, status=400)

        filters = {}

        for filter_index in ['hand', 'finger_index', 'segment_type']:
            filter_data = form.cleaned_data[filter_index]

            if filter_data is not None:
                filters[filter_index] = filter_data

        finger = Finger.objects.filter(**filters).first()

        if finger:
            return JsonResponse({'id': finger.id})

        return JsonResponse({'error': 'No matching finger found'}, status=404)


@method_decorator(csrf_exempt, name='dispatch')
class UpdateBaselineView(GetPostView):
    def create(self, data):
        form = UpdateBaselineForm(data)

        if not form.is_valid():
            return JsonResponse({'error': 'Invalid input.'}, status=400)

        target_id = form.cleaned_data['target_id']
        target_type = form.cleaned_data['target_type']
        baseline_x = form.cleaned_data['baseline_x']
        baseline_y = form.cleaned_data['baseline_y']
        baseline_z = form.cleaned_data['baseline_z']

        try:
            if target_type == 0:
                parts = Finger.objects.get(id=target_id)
            else:
                parts = HeadArmLegBody.objects.get(id=target_id)

            parts.baseline_x = baseline_x
            parts.baseline_y = baseline_y
            parts.baseline_z = baseline_z

            parts.save()
            return JsonResponse({'status': 'success', 'message': 'Baseline data updated successfully'})
        except Finger.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Finger not found'}, status=404)
        except HeadArmLegBody.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'HeadArmLegBody not found'}, status=404)

        return JsonResponse({'status': 'error', 'message': 'Invalid input'}, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class ActionLogView(GetPostView):
    def create(self, data):
        form = ActionLogForm(data)

        if not form.is_valid():
            return JsonResponse({'error': 'Invalid input'}, status=400)

        try:
            finger = Finger.objects.get(id=form.cleaned_data['finger_id'])
        except Finger.DoesNotExist:
            return JsonResponse({'error': 'Finger not found'}, status=404)

        x = form.cleaned_data['x']
        y = form.cleaned_data['y']
        z = form.cleaned_data['z']

        action_log = ActionLog.objects.create(finger=finger, x=x, y=y, z=z)

        return JsonResponse({
            "finger": action_log.finger.to_dict(),
            "coordinates": {
                "x": action_log.x,
                "y": action_log.y,
                "z": action_log.z
            },
            "timestamp": action_log.timestamp.isoformat()
        }, status=201)
