from django import forms


class FingerForm(forms.Form):
    hand = forms.IntegerField(required=True)
    finger_index = forms.IntegerField(required=True)


class SegmentForm(forms.Form):
    finger_id = forms.IntegerField(required=True)
    segment_type = forms.IntegerField(required=True)
    x = forms.FloatField(required=True)
    y = forms.FloatField(required=True)
    z = forms.FloatField(required=True)
