# forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password


class RegistroForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

#Hecho por JASON

# ----  NUEVO: Formulario de restablecimiento sin e‑mail  ----

User = get_user_model()

class PasswordSelfResetForm(forms.Form):
    identifier = forms.CharField(
        label="Usuario o correo",
        widget=forms.TextInput(attrs={
            "class": "form-input",
            "placeholder": "Usuario o correo"
        })
    )
    new_password1 = forms.CharField(
        label="Nueva contraseña",
        strip=False,
        widget=forms.PasswordInput(attrs={"class": "form-input"}),
    )
    new_password2 = forms.CharField(
        label="Confirmar contraseña",
        strip=False,
        widget=forms.PasswordInput(attrs={"class": "form-input"}),
    )

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get("new_password1")
        p2 = cleaned.get("new_password2")

        if p1 and p2 and p1 != p2:
            self.add_error("new_password2", "Las contraseñas no coinciden")

        if p1:
            validate_password(p1)

        ident = cleaned.get("identifier")
        qs = User.objects.filter(username=ident) | User.objects.filter(email__iexact=ident)
        if not qs.exists():
            self.add_error("identifier", "No existe un usuario con ese nombre o correo")
        else:
            cleaned["user"] = qs.first()

        return cleaned
