# views.py
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
#Parte de estilo
def index(request):
    return render(request, 'usuarios/index.html')
#HECHO POR JASON