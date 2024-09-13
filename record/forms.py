from django import forms
from .models import ImageLog


class FingerForm(forms.Form):
    hand = forms.IntegerField(required=True)
    finger_index = forms.IntegerField(required=True)
    segment_type = forms.IntegerField(required=True)
    baseline_x = forms.FloatField(required=False)
    baseline_y = forms.FloatField(required=False)
    baseline_z = forms.FloatField(required=False)


class UpdateBaselineForm(forms.Form):
    target_id = forms.IntegerField(required=True)
    target_type = forms.IntegerField(required=True)
    baseline_x = forms.FloatField(required=True)
    baseline_y = forms.FloatField(required=True)
    baseline_z = forms.FloatField(required=True)


class ActionLogForm(forms.Form):
    target_id = forms.IntegerField(required=True)
    target_type = forms.IntegerField(required=True)
    x = forms.FloatField(required=True)
    y = forms.FloatField(required=True)
    z = forms.FloatField(required=True)
    timestamp = forms.IntegerField(required=True)


class ImageLogForm(forms.ModelForm):
    class Meta:
        model = ImageLog
        fields = ['image']
