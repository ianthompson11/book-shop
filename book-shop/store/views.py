# Importación de herramientas necesarias de Django
from django.shortcuts import render  # Para renderizar templates HTML
from django.http import JsonResponse  # Para devolver respuestas JSON (APIs)
from django.views.decorators.csrf import csrf_exempt  # Para permitir POST sin token CSRF (usado con JS)
from django.contrib.auth.decorators import login_required  # Para proteger vistas que requieren login
from productos.models import Product  # Usar el modelo de productos
from .models import Order, OrderItem  # Importación de modelos propios
import json  # Para decodificar el cuerpo de las peticiones JSON

# -----------------------------------
# Vista que muestra los productos
# -----------------------------------
def product_list(request):
    products = Product.objects.all()  # Obtiene todos los productos de la base de datos
    return render(request, 'productos/product_list.html', {'products': products})  # Los pasa al template para mostrarlos

# -----------------------------------
# Vista que muestra el resumen del carrito
# -----------------------------------
def confirm_order(request):
    return render(request, 'store/confirm_order.html')  # Renderiza el HTML con el contenido del carrito (desde localStorage)

# -----------------------------------
# Vista que crea una orden en base al carrito (POST desde JS)
# -----------------------------------
@csrf_exempt  # Desactiva protección CSRF para permitir solicitudes JS sin token (solo en desarrollo)
def create_order(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)  # Decodifica el JSON recibido
            cart = data.get('cart', [])  # Extrae la lista de productos del carrito

            if not cart:
                return JsonResponse({'error': 'El carrito está vacío.'}, status=400)

            # Si el usuario está autenticado, se asocia a la orden
            user = request.user if request.user.is_authenticated else None

            # Se crea la orden vacía
            order = Order.objects.create(user=user, total=0)
            total = 0  # Acumulador del total de la compra

            # Itera sobre cada producto del carrito
            for item in cart:
                product_id = item['id']  # Usar ID en lugar de SKU
                quantity = item['quantity']
                product = Product.objects.get(id=product_id)  # Busca el producto real en la BD por ID
                item_total = product.price * quantity
                total += item_total  # Suma al total general

                # Crea el registro del producto dentro de la orden
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price=product.price
                )

                # Resta el stock del producto vendido (solo para productos físicos)
                if hasattr(product, 'product_type') and product.product_type == 'physical':
                    if product.stock >= quantity:
                        product.stock -= quantity
                        product.save()
                elif product.stock >= quantity:
                    # Para productos sin product_type pero con stock
                    product.stock -= quantity
                    product.save()

            # Asigna el total a la orden y guarda
            order.total = total
            order.save()

            return JsonResponse({'message': 'Orden creada correctamente.', 'order_id': order.id})  # Respuesta exitosa

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)  # Manejo de errores

    return JsonResponse({'error': 'Método no permitido'}, status=405)  # Solo acepta POST

# -----------------------------------
# Vista que muestra las órdenes de un usuario autenticado
# -----------------------------------
@login_required  # Solo usuarios logueados pueden ver sus órdenes
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')  # Obtiene las órdenes más recientes del usuario
    return render(request, 'store/my_orders.html', {'orders': orders})  # Renderiza el historial en una plantilla

# -----------------------------------
# Vista para mostrar el carrito de compras
# -----------------------------------
def cart_view(request):
    return render(request, 'store/cart.html')


