from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.shortcuts import render, redirect
from django.views import View
from .models import Keyframe
from .forms import *


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
