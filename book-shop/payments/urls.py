from django.urls import path
from . import views

urlpatterns = [
    path('payments/', views.index, name='payments'), #Usa el def index en views.py de payments
    path('final-confirm/', views.confirm_order, name='confirm_order'),
    path("order-success/", views.order_success, name="order_success"),
    path('api/orders/', views.create_order, name='create_order'), #Usa el django rest framework 
    path('api/orders/<str:order_id>/capture/', views.capture_order, name='capture_order'), #Usa el django rest framework 
    path('api/marcar-compra/', views.confirm_purchase, name='confirm_purchase'), # Nueva ruta para confirmar compra
    path('api/test-order/', views.test_order_creation, name='test_order_creation'), # Ruta de prueba
]

