from django import forms


class DataSearch(forms.Form):
    cities = forms.MultipleChoiceField(
        label='Sectores', choices=[('', 'Seleccionar')],
        error_messages={'required': 'Debes escoger al menos un sector.'},
        widget=forms.SelectMultiple(attrs={
            'class': 'form-control multiselect'}))
    start = forms.DateField(
        label='Fecha inicial',
        error_messages={'required': 'La fecha de inicio es obligatoria.'},
        widget=forms.TextInput(
            attrs={'class': 'form-control datepicker-history'}))
    end = forms.DateField(
        label='Fecha final',
        error_messages={'required': 'La fecha final es obligatoria.'},
        widget=forms.TextInput(
            attrs={'class': 'form-control datepicker-history'}))


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
