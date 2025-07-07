# Importación del módulo para definir modelos en Django
from django.db import models

# ----------------------------
# MODELO DE PRODUCTO
# ----------------------------
class Product(models.Model):
    name = models.CharField(max_length=100)  # Nombre del producto (máximo 100 caracteres)
    description = models.TextField()  # Descripción detallada del producto
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Precio con hasta 10 dígitos y 2 decimales
    sku = models.CharField(max_length=100, unique=True)  # Código único para identificar el producto
    stock = models.IntegerField()  # Cantidad disponible en inventario
    image = models.ImageField(upload_to='products/', blank=True, null=True)  # Imagen del producto (opcional)

    def __str__(self):
        # Representación legible del producto en el panel de administración
        return self.name

# ----------------------------
# MODELO DE ORDEN DE COMPRA
# ----------------------------

from django.contrib.auth.models import User  # Importación del modelo de usuario para asociarlo a la orden

# Opciones de estado de una orden
ORDER_STATUS = [
    ('pending', 'Pendiente'),
    ('completed', 'Completado'),
    ('cancelled', 'Cancelado'),
]

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)  # Usuario que realiza la orden (puede quedar nulo si no está autenticado)
    created_at = models.DateTimeField(auto_now_add=True)  # Fecha de creación de la orden (automáticamente)
    status = models.CharField(max_length=10, choices=ORDER_STATUS, default='pending')  # Estado actual de la orden
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Monto total de la orden

    def __str__(self):
        # Muestra la orden como "Orden #id - estado"
        return f"Orden #{self.id} - {self.status}"

# ----------------------------
# MODELO DE DETALLES DE CADA PRODUCTO EN UNA ORDEN
# ----------------------------
class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)  # Relación con la orden principal
    product = models.ForeignKey(Product, on_delete=models.CASCADE)  # Producto relacionado
    quantity = models.PositiveIntegerField(default=1)  # Cantidad de ese producto comprado
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Precio del producto en ese momento

    def subtotal(self):
        # Calcula el subtotal de este producto (precio x cantidad)
        return self.quantity * self.price

    def __str__(self):
        # Muestra algo como "Zapato x2"
        return f"{self.product.name} x{self.quantity}"


