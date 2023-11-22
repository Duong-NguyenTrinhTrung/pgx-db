from django import forms
from django.forms import NumberInput


class FilterForm(forms.Form):
    mean_vep_score = forms.DecimalField(
        required=False,
        widget=NumberInput(
            attrs={'class': 'form-control-range', 'step': 0.1, 'min': 0, 'max': 1, 'type': 'range'},
        )
    )
