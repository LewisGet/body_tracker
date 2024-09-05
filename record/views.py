from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from .models import Finger, Segment
from .forms import FingerForm, SegmentForm
import json


@method_decorator(csrf_exempt, name='dispatch')
class FingerView(View):
    def get(self, request):
        form = FingerForm(request.GET)

        if not form.is_valid():
            return JsonResponse({'error': 'Invalid input. Both hand and finger_index must be integers.'}, status=400)

        hand = form.cleaned_data['hand']
        finger_index = form.cleaned_data['finger_index']

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
class SegmentView(View):
    def get(self, request):
        data = request.GET

        return self.create(data)

    def post(self, request):
        data = json.loads(request.body)

        return self.create(data)

    def create(self, data):
        form = SegmentForm(data)

        if not form.is_valid():
            return JsonResponse({'error': 'Invalid input'}, status=400)

        try:
            finger = Finger.objects.get(id=form.cleaned_data['finger_id'])
        except Finger.DoesNotExist:
            return JsonResponse({'error': 'Finger not found'}, status=404)

        segment_type = form.cleaned_data['segment_type']

        x = form.cleaned_data['x']
        y = form.cleaned_data['y']
        z = form.cleaned_data['z']

        segment = Segment.objects.create(finger=finger, segment_type=segment_type, x=x, y=y, z=z)

        return JsonResponse({
            "finger": segment.finger.to_dict(),
            "segment_type": segment.get_segment_type_display(),
            "coordinates": {
                "x": segment.x,
                "y": segment.y,
                "z": segment.z
            },
            "timestamp": segment.timestamp.isoformat()
        }, status=201)
