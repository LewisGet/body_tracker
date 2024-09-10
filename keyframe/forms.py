from django import forms
from .models import Keyframe


class KeyframeForm(forms.ModelForm):
    class Meta:
        model = Keyframe
        fields = ['timestamp', 'description']
