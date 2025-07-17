# Importa las herramientas necesarias del panel de administración de Django
from django.contrib import admin
# Importa los modelos que se van a registrar en el panel de administración
from .models import Product, Order, OrderItem

# -----------------------------------------------
# Configura la visualización de los productos dentro de una orden
# -----------------------------------------------
class OrderItemInline(admin.TabularInline):
    model = OrderItem  # Modelo relacionado que se mostrará en forma tabular dentro de la orden
    readonly_fields = ('product', 'quantity', 'price')  # Solo lectura: no se pueden editar aquí
    extra = 0  # No se muestra ninguna fila vacía adicional

# -----------------------------------------------
# Configura cómo se muestra el modelo Order en el admin
# -----------------------------------------------
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at', 'status', 'total')  # Columnas visibles en la lista de órdenes
    list_filter = ('status', 'created_at')  # Filtros laterales para facilitar búsqueda
    inlines = [OrderItemInline]  # Muestra los productos asociados directamente dentro de la orden

# -----------------------------------------------
# Registro de modelos en el panel de administración
# -----------------------------------------------
admin.site.register(Product)  # Activa la administración del modelo Product
admin.site.register(Order, OrderAdmin)  # Usa la configuración personalizada de OrderAdmin



