from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import Keyframe
from .forms import KeyframeForm


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
