from django.urls import path
from . import views

urlpatterns = [
    path('payments/', views.index, name='index'), #Usa el def index en views.py de payments
    path('api/orders/', views.create_order, name='create_order'), #Usa el django rest framework 
    path('api/orders/<str:order_id>/capture/', views.capture_order, name='capture_order'), #Usa el django rest framework 
]
