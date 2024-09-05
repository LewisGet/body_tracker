from django import forms


class FingerForm(forms.Form):
    hand = forms.IntegerField(required=True)
    finger_index = forms.IntegerField(required=True)
    segment_type = forms.IntegerField(required=True)
    baseline_x = forms.FloatField(required=False)
    baseline_y = forms.FloatField(required=False)
    baseline_z = forms.FloatField(required=False)


class ActionLogForm(forms.Form):
    finger_id = forms.IntegerField(required=True)
    x = forms.FloatField(required=True)
    y = forms.FloatField(required=True)
    z = forms.FloatField(required=True)
