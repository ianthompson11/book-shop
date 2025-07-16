# Importa la función path para definir rutas URL
from django.urls import path

# Importa el archivo views.py para conectar las rutas con sus respectivas vistas
from . import views

# Lista de rutas definidas para la app 'store'
urlpatterns = [

    # Redirect main products route to productos app
    path('products/', views.products_redirect, name='products_redirect'),

    # Ruta para confirmar el contenido del carrito
    path('confirm-order/', views.confirm_order, name='confirm_order'),

    # Ruta que recibe la solicitud POST con el carrito y crea la orden en la base de datos
    path('create-order/', views.create_order, name='create_order'),

    # Ruta para que el usuario autenticado vea su historial de órdenes
    path('my-orders/', views.my_orders, name='my_orders'),

    path('cart/', views.cart_view, name='cart_view'),  # Vista del carrito visual

]

