# urls.py
from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    path('', views.index, name='index'),# <--- Página principal
    path('registro/', views.registro, name='registro'),
    path('login/', views.iniciar_sesion, name='login'),
    path('logout/', views.cerrar_sesion, name='logout'),
    path('panel/', views.panel_usuario, name='panel'),
]
# Hecho por JASON
