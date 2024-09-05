from django import forms


class FingerForm(forms.Form):
    hand = forms.IntegerField(required=True)
    finger_index = forms.IntegerField(required=True)
