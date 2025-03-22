from django import forms


class DataSearch(forms.Form):
    cities = forms.MultipleChoiceField(
        label='Comunas', choices=[], required=True,
        widget=forms.SelectMultiple(attrs={
            'class': 'form-control multiselect'}))
    years = forms.MultipleChoiceField(
        label='Años', choices=[], required=True,
        widget=forms.SelectMultiple(attrs={
            'class': 'form-control multiselect'}))


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
