from django import forms
from .models import Policy, PolicyStatus
from django.contrib.auth.models import User

class PolicyForm(forms.ModelForm):

    class Meta:
        model = Policy
        fields = ('status', 'owner')
        widgets = {
            'status': forms.Select(attrs={'class':'form-control mt-2 mb-2','required':False}),
            'owner': forms.Select(attrs={'class':'form-control mt-2 mb-2', 'placeholder':'Nombre Titular','required':False})
        }
    def __init__(self, *args, **kwargs):
        super(PolicyForm, self).__init__(*args, **kwargs)
        self.fields['status'].empty_label = "(Seleciona un estado de la póliza)"
        self.fields['owner'].empty_label = "(Seleciona al titular)"