from django.urls import path
from . import views

urlpatterns = [
    path('', views.productos_view, name='productos'), # Vista principal de productos
    path('lista/', views.product_list, name='product_list'),  # Lista de productos
    path('detalle/<int:pk>/', views.product_detail, name='product_detail'),  # Detalle de un producto
    path('crear/', views.product_create, name='product_create'),  # Crear producto
    path('editar/<int:pk>/', views.product_update, name='product_update'),  # Editar producto
    path('eliminar/<int:pk>/', views.product_delete, name='product_delete'),  # Eliminar producto
]