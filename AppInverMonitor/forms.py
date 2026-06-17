from django import forms
from django.contrib.auth.models import User
from .models import PerfilUsuario
from django.contrib.auth import authenticate

class RegistrarUsuarioForm(forms.ModelForm):
    nombre    = forms.CharField(max_length=100, required=True,  label='Nombre')
    telefono  = forms.CharField(max_length=20,  required=False, label='Teléfono')
    correo    = forms.EmailField(required=True, label='Correo')
    password1 = forms.CharField(widget=forms.PasswordInput, label='password1')
    password2 = forms.CharField(widget=forms.PasswordInput, label='password2')

    class Meta:
        model  = User
        fields = []

    def clean_correo(self):
        correo = self.cleaned_data['correo']
        if User.objects.filter(email=correo).exists():
            raise forms.ValidationError("Este correo ya está registrado.")
        return correo

    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        if telefono and PerfilUsuario.objects.filter(telefono=telefono).exists():
            raise forms.ValidationError("Este teléfono ya está registrado.")
        return telefono

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password1')
        p2 = cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['correo']
        user.email    = self.cleaned_data['correo']
        user.set_password(self.cleaned_data['password1'])

        if commit:
            user.save()
            perfil, created = PerfilUsuario.objects.get_or_create(
                usuario=user,
                defaults={
                    'nombre':   self.cleaned_data['nombre'],
                    'telefono': self.cleaned_data.get('telefono', ''),
                }
            )
            if not created:
                perfil.nombre   = self.cleaned_data['nombre']
                perfil.telefono = self.cleaned_data.get('telefono', '')
                perfil.save()
        return user
    

class LoginForm(forms.Form):
    email = forms.EmailField(
        label='Correo electrónico',
        max_length=254,
        widget=forms.EmailInput(attrs={
            'id': 'email',
            'class': 'field-input',
            'placeholder': 'correo@empresa.com',
            'autocomplete': 'email',
        })
    )
 
    password = forms.CharField(
        label='Contraseña',
        strip=False,  
        widget=forms.PasswordInput(attrs={
            'id': 'password',
            'class': 'field-input',
            'placeholder': '••••••••',
            'autocomplete': 'current-password',
        })
    )
 
    remember_me = forms.BooleanField(
        required=False,  
        label='Recordarme',
        widget=forms.CheckboxInput(attrs={
            'id': 'remember',
            'name': 'remember',
        })
    )
 
    # Guardamos el usuario autenticado 
    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)
 
    def clean(self):
        cleaned_data = super().clean()
        email    = cleaned_data.get('email')
        password = cleaned_data.get('password')
 
        if email and password:
            # Django autentica por username por defecto
            self.user_cache = authenticate(
                self.request,
                username=email,
                password=password,
            )
 
            if self.user_cache is None:
                raise forms.ValidationError(
                    'Correo o contraseña incorrectos.',
                    code='invalid_login',
                )
 
            if not self.user_cache.is_active:
                raise forms.ValidationError(
                    'Esta cuenta está desactivada.',
                    code='inactive',
                )
 
        return cleaned_data
 
    def get_user(self):
        """Retorna el usuario autenticado para usarlo en la view."""
        return self.user_cache
 