from django import forms


class LayerControlForm(forms.Form):
    green = forms.BooleanField(
        required=False,
        initial=False
    )
    orange = forms.BooleanField(
        required=False,
        initial=True
    )
    red = forms.BooleanField(
        required=False,
        initial=True
    )
