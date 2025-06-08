from django import forms
from .models import Edital, CicloDeEstudo

class EditalForm(forms.ModelForm):
    class Meta:
        model = Edital
        fields = ['title', 'content']

class CicloDeEstudoForm(forms.ModelForm):
    class Meta:
        model = CicloDeEstudo
        fields = ['title', 'start_date', 'end_date']