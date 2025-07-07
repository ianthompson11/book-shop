from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import Product, Order, OrderItem
import json


def product_list(request):
    products = Product.objects.all()
    return render(request, 'store/product_list.html', {'products': products})

def confirm_order(request):
    return render(request, 'store/confirm_order.html')

# --- Nueva función para crear orden desde el carrito ---
@csrf_exempt
def create_order(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            cart = data.get('cart', [])

            if not cart:
                return JsonResponse({'error': 'El carrito está vacío.'}, status=400)

            user = request.user if request.user.is_authenticated else None

            order = Order.objects.create(user=user, total=0)
            total = 0

            for item in cart:
                sku = item['sku']
                quantity = item['quantity']
                product = Product.objects.get(sku=sku)
                item_total = product.price * quantity
                total += item_total

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price=product.price
                )

                product.stock -= quantity
                product.save()

            order.total = total
            order.save()

            return JsonResponse({'message': 'Orden creada correctamente.', 'order_id': order.id})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Método no permitido'}, status=405)

# --- Nueva vista para "Mis Órdenes" ---
@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'store/my_orders.html', {'orders': orders})

