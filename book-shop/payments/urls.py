from django.urls import path
from . import views

urlpatterns = [
    #path('', views.index, name='payments_home'),  # para /payments/
    #path('pay', views.pay, name = 'pay'), #para ventana de pay que se abre al presionar el boton de pagar
    path('', views.index, name='index'),
    path('api/orders/', views.create_order, name='create_order'),
    path('api/orders/<str:order_id>/capture/', views.capture_order, name='capture_order'),
]
