from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.models import Avg
from django.db import transaction
from django.views import View
from .models import *
from .forms import *
import datetime
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

    def dispatch(self, request, *args, **kwargs):
        api_control = ApiControl.objects.first()

        if not api_control or not api_control.is_enabled:
            return JsonResponse({'error': 'API read/write is currently disabled'}, status=403)

        return super().dispatch(request, *args, **kwargs)


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
class CreateActionLogView(GetPostView):
    def create(self, data):
        form = ActionLogForm(data)

        if not form.is_valid():
            return JsonResponse({'error': 'Invalid input'}, status=400)

        target_id = form.cleaned_data['target_id']
        target_type = form.cleaned_data['target_type']
        x = form.cleaned_data['x']
        y = form.cleaned_data['y']
        z = form.cleaned_data['z']
        timestamp = form.cleaned_data['timestamp']
        timestamp = datetime.datetime.fromtimestamp(timestamp / 1000)

        try:
            if target_type == 0:
                parts = Finger.objects.get(id=target_id)
                action_log = ActionLog.objects.create(finger=parts, x=x, y=y, z=z, timestamp=timestamp)
            else:
                parts = HeadArmLegBody.objects.get(id=target_id)
                action_log = ActionLog.objects.create(head_arm_leg_body=parts, x=x, y=y, z=z, timestamp=timestamp)

        except Finger.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Finger not found'}, status=404)
        except HeadArmLegBody.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'HeadArmLegBody not found'}, status=404)

        return JsonResponse({
            "target_id": target_id,
            "target_type": parts._meta.model_name,
            "coordinates": {
                "x": action_log.x,
                "y": action_log.y,
                "z": action_log.z
            },
            "timestamp": action_log.timestamp.isoformat()
        }, status=201)


@method_decorator(csrf_exempt, name='dispatch')
class BatchCreateActionLogView(GetPostView):
    def create(self, data):
        def list_format(value, type_function):
            return [type_function(d) for d in value.split(",")]


        try:
            with transaction.atomic():
                target_ids = list_format(data['target_id'], int)
                target_types = list_format(data['target_type'], int)
                timestamps = list_format(data['timestamp'], int)

                if len(target_ids) == 1:
                    target_ids = [target_ids[0] for i in range(len(timestamps))]

                if len(target_types) == 1:
                    target_types = [target_types[0] for i in range(len(timestamps))]



                for target_id, target_type, x, y, z, timestamp in zip(
                    target_ids,
                    target_types,
                    list_format(data['x'], float),
                    list_format(data['y'], float),
                    list_format(data['z'], float),
                    timestamps
                ):
                    data_dict = {
                        "target_id": target_id,
                        "target_type": target_type,
                        "x": x,
                        "y": y,
                        "z": z,
                        "timestamp": timestamp,
                    }
                    form = ActionLogForm(data_dict)

                    timestamp = datetime.datetime.fromtimestamp(timestamp / 1000)

                    if not form.is_valid():
                        raise ValueError('Invalid input')

                    if target_type == 0:
                        parts = Finger.objects.get(id=target_id)
                        action_log = ActionLog.objects.create(finger=parts, x=x, y=y, z=z, timestamp=timestamp)
                    else:
                        parts = HeadArmLegBody.objects.get(id=target_id)
                        action_log = ActionLog.objects.create(head_arm_leg_body=parts, x=x, y=y, z=z, timestamp=timestamp)
        except Finger.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Finger not found'}, status=404)
        except HeadArmLegBody.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'HeadArmLegBody not found'}, status=404)
        except ValueError as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

        return JsonResponse({"message": "done"}, status=201, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
class CreateImageLogView(GetPostView):
    def get(self, request):
        form = ImageLogForm()

        return render(request, 'base_form.html', {'form': form})

    def post(self, request):
        form = ImageLogForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()

        return redirect('create_image_log')


@method_decorator(csrf_exempt, name='dispatch')
class ResetLogView(View):
    def get(self, request):
        confirm = str(request.GET.get('confirm', "false")) == "true"

        if not confirm:
            return JsonResponse({'status': 'error', 'message': 'stop reset'}, status=500)

        ActionLog.objects.all().delete()
        ImageLog.objects.all().delete()

        return JsonResponse({'status': 'done'}, status=201)


@method_decorator(csrf_exempt, name='dispatch')
class ToggleApiView(View):
    def get(self, request, *args, **kwargs):
        api_control = ApiControl.objects.first()

        if not api_control:
            api_control = ApiControl.objects.create(is_enabled=False)

        api_control.is_enabled = not api_control.is_enabled
        api_control.save()

        return JsonResponse({'status': 'done. now status is: ' + str(api_control.is_enabled)}, status=201)


@method_decorator(csrf_exempt, name='dispatch')
class ScanLocationView(View):
    def get(self, request):
        return JsonResponse({'status': 'done'}, status=200)


@method_decorator(csrf_exempt, name='dispatch')
class HardwareStatusView(View):
    def get(self, request):
        last_contact = datetime.datetime.now() - datetime.timedelta(seconds=3)

        fingers = Finger.objects.all()
        body_parts = HeadArmLegBody.objects.all()

        result = []

        for finger in fingers:
            has_recent_log = ActionLog.objects.filter(finger=finger, timestamp__gte=last_contact).exists()
            result.append({
                'id': finger.id,
                'content': finger.to_dict(),
                'connect': has_recent_log,
                'is_body': False
            })

        for part in body_parts:
            has_recent_log = ActionLog.objects.filter(head_arm_leg_body=part, timestamp__gte=last_contact).exists()
            result.append({
                'id': part.id,
                'content': part.to_dict(),
                'connect': has_recent_log,
                'is_body': True
            })

        return render(request, 'hardware_status.html', {'result': result})


@method_decorator(csrf_exempt, name='dispatch')
class SetupBaselineView(View):
    def get(self, request):
        all_finger = Finger.objects.all().order_by('id')
        all_body = HeadArmLegBody.objects.all().order_by('id')
        all_logs = ActionLog.objects.all().order_by('timestamp')
        last_timestamp = all_logs[len(all_logs) - 1].timestamp

        start = last_timestamp - datetime.timedelta(seconds=8)
        end = last_timestamp - datetime.timedelta(seconds=3)

        all_logs = all_logs.filter(timestamp__range=(start, end))
        all_finger_logs = all_logs.filter(finger__isnull=False)
        all_body_logs = all_logs.filter(head_arm_leg_body__isnull=False)

        for finger in all_finger:
            this_finger_logs = all_finger_logs.filter(finger=finger)

            avg_x = this_finger_logs.aggregate(Avg('x'))['x__avg']
            avg_y = this_finger_logs.aggregate(Avg('y'))['y__avg']
            avg_z = this_finger_logs.aggregate(Avg('z'))['z__avg']

            finger.baseline_x = avg_x
            finger.baseline_y = avg_y
            finger.baseline_z = avg_z
            finger.save()

        for body_part in all_body:
            this_body_logs = all_body_logs.filter(head_arm_leg_body=body_part)

            avg_x = this_body_logs.aggregate(Avg('x'))['x__avg']
            avg_y = this_body_logs.aggregate(Avg('y'))['y__avg']
            avg_z = this_body_logs.aggregate(Avg('z'))['z__avg']

            body_part.baseline_x = avg_x
            body_part.baseline_y = avg_y
            body_part.baseline_z = avg_z
            body_part.save()

        return JsonResponse({'status': 'done'}, status=200)
