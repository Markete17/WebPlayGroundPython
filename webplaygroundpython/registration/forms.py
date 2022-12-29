from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile

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

class ProfileForm(forms.ModelForm):
    
    class Meta:
        model = Profile
        fields = ('avatar', 'bio', 'link')
        widgets = {
            'avatar': forms.ClearableFileInput(attrs={'class': 'form-control-file mt-3'}),
            'bio': forms.Textarea(attrs={'class': 'form-control mt-3', 'rows': 1, 'placeholder': 'Biografía'}),
            'link': forms.URLInput(attrs={'class': 'form-control mt-3', 'placeholder': 'Enlace'})
        }

class EmailForm(forms.ModelForm):
    
    email = forms.EmailField(required=True, help_text='Requerido, 254 carácteres como máximo y debe ser válido.')

    class Meta:
        model = User
        fields = ['email']
    
    def clean_email(self):
        
        # Con esto se recupera el email que ha puesto el usuario antes de que se procese el formulario
        email = self.cleaned_data.get("email")

        if 'email' in self.changed_data: #para comprobar que el campo email del formulario ha cambiado
            if User.objects.filter(email=email).exists():
                raise forms.ValidationError('El email ya está registrado, prueba con otro')
        return email

