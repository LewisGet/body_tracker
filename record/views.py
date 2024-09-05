from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from .models import Finger, Segment
import json


@method_decorator(csrf_exempt, name='dispatch')
class SegmentView(View):
    def get(self, request):
        data = request.GET

        return self.create(data)

    def post(self, request):
        data = json.loads(request.body)

        return self.create(data)

    def create(self, data):
        finger_id = data.get('finger_id')
        segment_type = data.get('segment_type')

        x = data.get('x')
        y = data.get('y')
        z = data.get('z')

        finger = Finger.objects.get(id=finger_id)
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
