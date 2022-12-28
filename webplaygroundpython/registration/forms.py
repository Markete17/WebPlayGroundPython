from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class UserCreationFormWithEmail(UserCreationForm):
    
    email = forms.EmailField(required=True, help_text='Requerido, 254 carácteres como máximo y debe ser válido.')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
   
    def clean_email(self):
        
        # Con esto se recupera el email que ha puesto el usuario antes de que se procese el formulario
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('El email ya está registrado, prueba con otro')
        return email