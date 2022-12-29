from .forms import UserCreationFormWithEmail
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django import forms
from django.views.generic.edit import UpdateView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from .models import Profile
from .forms import ProfileForm, EmailForm

class SignUpCreateView(CreateView):
    form_class = UserCreationFormWithEmail
    template_name = 'registration/signup.html'

    def get_success_url(self):
        return reverse_lazy('login')+'?register'

    def get_form(self, form_class=None):
        form = super().get_form()
        # Modificar el formulario a tiempo real
        form.fields['username'].widget = forms.TextInput(
            attrs={'class':'form-control mb-2', 
            'placeholder':'Nombre de usuario'}
            )
        form.fields['email'].widget = forms.EmailInput(
            attrs={'class':'form-control mb-2', 
            'placeholder':'Dirección email'}
            )
        form.fields['password1'].widget = forms.PasswordInput(
            attrs={'class':'form-control mb-2', 
            'placeholder':'Contraseña'}
            )
        form.fields['password2'].widget = forms.PasswordInput(
            attrs={'class':'form-control mb-2', 
            'placeholder':'Confirmar Contraseña'}
            )
        return form

@method_decorator(login_required, name='dispatch')
class ProfileUpdateView(UpdateView):
    # model = Profile no es necesario se indica en el form
    form_class = ProfileForm
    success_url = reverse_lazy('profile')

    def get_object(self):
        profile, created = Profile.objects.get_or_create(user=self.request.user)
        return profile

@method_decorator(login_required, name='dispatch')
class EmailUpdateView(UpdateView):
    form_class = EmailForm
    success_url = reverse_lazy('profile')
    template_name = 'registration/profile_email_form.html'

    def get_object(self):
        return self.request.user
    
    def get_form(self, form_class=None):
        
        form = super().get_form()
        
        # Modificar el formulario a tiempo real y así no quitar validaciones de Django
        form.fields['email'].widget = forms.EmailInput(
            attrs={'class':'form-control mb-2', 
            'placeholder':'Email'}
            )
        return form