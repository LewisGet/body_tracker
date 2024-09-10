from django import forms
from .models import Keyframe
from record.models import ImageLog


class KeyframeForm(forms.ModelForm):
    class Meta:
        model = Keyframe
        fields = ['timestamp', 'description']


class BatchKeyframeForm(forms.Form):
    timestamps = forms.ModelMultipleChoiceField(
        queryset=ImageLog.objects.all().order_by('timestamp'),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="Select Timestamps"
    )
