"""from django import forms
from .models import Policy, PolicyStatus
from django.contrib.auth.models import User

class PolicyListViewForm(forms.ModelForm):

    class Meta:
        model = Policy
        fields = ('policy_code', 'status', 'owner', 'cancellation_date', 'suspension_date', 'created')
        widgets = {
            'policy_code': forms.TextInput(attrs={'class':'form-control', 'placeholder':'Número Póliza','required':False}),
            'status': forms.Select(attrs={'class':'form-control','required':False}),
            'cancellation_date': forms.DateInput(attrs={'class':'form-control','required':False}),
            'created': forms.DateInput(attrs={'class':'form-control','required':False}),
            'suspension_date': forms.DateInput(attrs={'class':'form-control','required':False}),
            'owner': forms.Select(attrs={'class':'form-control', 'placeholder':'Nombre Titular','required':False})
        }
    def __init__(self, *args, **kwargs):
        # first call parent's constructor
        super(PolicyListViewForm, self).__init__(*args, **kwargs)
        # there's a `fields` property now
        self.fields['cancellation_date'].required = False
        self.fields['created'].required = False
        self.fields['suspension_date'].required = False
        self.fields['owner'].required = False
        self.fields['status'].required = False
        self.fields['policy_code'].required = False
    
"""