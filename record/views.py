from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from .models import *
from .forms import *
import json


@method_decorator(csrf_exempt, name='dispatch')
class FingerView(View):
    def get(self, request):
        form = FingerForm(request.GET)

        if not form.is_valid():
            return JsonResponse({'error': 'Invalid input. Both hand and finger_index must be integers.'}, status=400)

        hand = form.cleaned_data['hand']
        finger_index = form.cleaned_data['finger_index']
        segment_type = form.cleaned_data['segment_type']

        filters = {}
        if hand is not None:
            filters['hand'] = hand

        if finger_index is not None:
            filters['finger_index'] = finger_index

        finger = Finger.objects.filter(**filters).first()

        if finger:
            return JsonResponse({'id': finger.id})

        return JsonResponse({'error': 'No matching finger found'}, status=404)


@method_decorator(csrf_exempt, name='dispatch')
class ActionLogView(View):
    def get(self, request):
        data = request.GET

        return self.create(data)

    def post(self, request):
        data = json.loads(request.body)

        return self.create(data)

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
