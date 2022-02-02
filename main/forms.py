from django import forms
from .models import *

class DescrForm(forms.Form):
    desc=forms.CharField(label="", required=True)
    min_mc = forms.FloatField(label="", required=False)
    max_mc = forms.FloatField(label="", required=False)
