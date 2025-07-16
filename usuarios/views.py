from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .forms import RegistroForm
from django.contrib.auth.models import User

# Si tienes acceso a la app ordenes:
# from ordenes.models import Orden

def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/')  # redirige a inicio o productos
    else:
        form = RegistroForm()
    return render(request, 'usuarios/registro.html', {'form': form})

def iniciar_sesion(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('/')
    else:
        form = AuthenticationForm()
    return render(request, 'usuarios/login.html', {'form': form})

def cerrar_sesion(request):
    logout(request)
    return redirect('usuarios:login')

@login_required
def panel_usuario(request):
    # ordenes = Orden.objects.filter(usuario=request.user)  # Solo si ya existe esa app
    ordenes = []  # Quita esto si tienes acceso al modelo Orden
    return render(request, 'usuarios/panel.html', {'ordenes': ordenes})

# Parte de estilo
def index(request):
    return render(request, 'usuarios/index.html')

# HECHO POR JASON

# --------------------------------------------------------------------
# NUEVO: Restablecimiento de contraseña sin correo
# --------------------------------------------------------------------
from django.views import View
from django.contrib import messages
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import login as auth_login
from .forms import PasswordSelfResetForm  # junto al resto de imports
from allauth.account.auth_backends import AuthenticationBackend  # Añadido para especificar el backend

class PasswordSelfResetView(View):
    template_name = "account/password_self_reset.html"

    def get(self, request):
        return render(request, self.template_name, {"form": PasswordSelfResetForm(), "ocultar_header": True})

    def post(self, request):
        form = PasswordSelfResetForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data["user"]
            user.set_password(form.cleaned_data["new_password1"])
            user.save()

            # Especifica el backend de allauth al hacer login
            auth_login(request, user, backend='allauth.account.auth_backends.AuthenticationBackend')
            messages.success(request, "Contraseña actualizada e inicio de sesión exitoso.")
            return redirect('/')  # se puede cambiar si se quiere otra ruta

        return render(request, self.template_name, {"form": form})