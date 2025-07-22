from django.shortcuts import render
from django.shortcuts import render, redirect
from .paypal_views import create_order, capture_order #Importa del archivo paypal_views.py sus funciones para no sobrepoblar views
from django.utils.cache import patch_cache_control #para evitar que recargue el sitio payments desde la cache
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from productos.models import Product  # Usar el modelo de productos
from store.models import Order, OrderItem
import json
import os
from dotenv import load_dotenv # libreria para cargar la variable del archivo .env #payments

load_dotenv() # comando para cargar la variable del archivo .env #payments
def index(request): 
    if not request.session.get("permitido_pago"):
        return redirect("/")

    del request.session["permitido_pago"]
    request.session['permitido_order_success'] = True

    response = render(request, "payments/index.html", {
        "PAYPAL_CLIENT_ID": os.getenv("PAYPAL_CLIENT_ID")
    })

    patch_cache_control(response, no_cache=True, no_store=True, must_revalidate=True)

    return response
    

# Esta seccion es para el sitio de confirmacion de la orden
def confirm_order(request):
    request.session['permitido_pago'] = True
    return render(request, "payments/confirm_order.html")

def order_success(request):
    if not request.session.get('permitido_order_success'):
        return redirect("/")  # Redirige al home si no tiene permiso

    # Borra el permiso para evitar reingreso o recarga
    del request.session['permitido_order_success']

    transaction_id = request.GET.get("transaction_id")
    status = request.GET.get("status")

    response = render(request, "payments/order_success.html", {
        "transaction_id": transaction_id,
        "status": status,
    })
    patch_cache_control(response, no_cache=True, no_store=True, must_revalidate=True)

    return response

@csrf_exempt
def confirm_purchase(request):
    """Vista para confirmar la compra y crear la orden después del pago de PayPal"""
    print("DEBUG: ===== INICIO CONFIRM_PURCHASE =====")
    print(f"DEBUG: Request method: {request.method}")
    print(f"DEBUG: Request.user: {request.user}")
    print(f"DEBUG: Request.user.is_authenticated: {request.user.is_authenticated}")
    
    if request.method == 'POST':
        try:
            print(f"DEBUG: Request.body raw: {request.body}")
            print(f"DEBUG: Request.POST: {request.POST}")
            
            if not request.body:
                print("DEBUG ERROR: Request.body está vacío")
                return JsonResponse({'error': 'No se recibieron datos'}, status=400)
            
            data = json.loads(request.body)
            transaction_id = data.get('transaction_id')
            status = data.get('status')
            cart_data = data.get('cart', [])

            print(f"DEBUG - Datos recibidos: {data}")  # Debug
            print(f"DEBUG - Carrito: {cart_data}")  # Debug

            if not cart_data:
                return JsonResponse({'error': 'No hay productos en el carrito.'}, status=400)

            # Si el usuario está autenticado, se asocia a la orden
            user = request.user if request.user.is_authenticated else None

            # Crear la orden
            order = Order.objects.create(
                user=user, 
                total=0, 
                status='completed'  # La orden ya está pagada
            )
            
            total = 0

            # Procesar cada producto del carrito
            for item in cart_data:
                try:
                    print(f"DEBUG - Procesando item: {item}")  # Debug
                    
                    # CORREGIR EL PROBLEMA: Los parámetros id y description están intercambiados
                    # Si el 'id' es una string larga, probablemente sea la description
                    # Si 'description' es un número, probablemente sea el ID real
                    item_id = item.get('id')
                    item_description = item.get('description')
                    
                    # Determinar el ID real basado en el tipo de datos
                    if isinstance(item_description, (int, str)) and str(item_description).isdigit():
                        # description es un número, probablemente es el ID real
                        product_id = int(item_description)
                        actual_description = item_id  # el 'id' es realmente la descripción
                        print(f"DEBUG - IDs intercambiados detectados. Usando description como ID: {product_id}")
                    elif isinstance(item_id, (int, str)) and str(item_id).isdigit():
                        # id es un número, usar como es
                        product_id = int(item_id)
                        actual_description = item_description
                        print(f"DEBUG - ID normal detectado: {product_id}")
                    else:
                        # Si no podemos determinar el ID, intentar buscar por nombre
                        product_id = None
                        print(f"DEBUG - No se pudo determinar ID, buscaremos por nombre: {item.get('name')}")
                    
                    print(f"DEBUG - Buscando producto con ID: {product_id}")  # Debug
                    
                    if product_id:
                        # Buscar el producto por ID
                        try:
                            product = Product.objects.get(id=product_id)
                            print(f"DEBUG - Producto encontrado por ID: {product.name}, Precio: {product.price}")  # Debug
                        except Product.DoesNotExist:
                            print(f"DEBUG - Producto con ID {product_id} no existe, buscando por nombre: {item['name']}")
                            product = Product.objects.get(name=item['name'])
                            print(f"DEBUG - Producto encontrado por nombre: {product.name}, ID real: {product.id}")  # Debug
                    else:
                        # Si no hay ID válido, intentar buscar por nombre como respaldo
                        product = Product.objects.get(name=item['name'])
                        print(f"DEBUG - Producto encontrado por nombre: {product.name}")  # Debug
                    
                    quantity = int(item.get('quantity', 1))
                    price = float(item.get('price', product.price))
                    item_total = price * quantity
                    total += item_total

                    print(f"DEBUG - Cantidad: {quantity}, Precio: {price}, Total item: {item_total}")  # Debug

                    # Crear el item de la orden
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=quantity,
                        price=price
                    )

                    # Actualizar el stock si es un producto físico
                    if hasattr(product, 'product_type') and product.product_type == 'physical':
                        if product.stock >= quantity:
                            product.stock -= quantity
                            product.save()
                    elif hasattr(product, 'stock') and product.stock >= quantity:
                        # Para productos que no tienen product_type pero sí stock
                        product.stock -= quantity
                        product.save()

                except Product.DoesNotExist:
                    # Si no se encuentra el producto, continuar con el siguiente
                    print(f"DEBUG - Producto no encontrado: {item}")  # Debug
                    continue
                except Exception as e:
                    print(f"DEBUG - Error procesando item: {e}")  # Debug
                    continue

            print(f"DEBUG - Total calculado: {total}")  # Debug

            # Actualizar el total de la orden
            order.total = total
            order.save()

            print(f"DEBUG - Orden guardada con ID: {order.id}, Total: {order.total}")  # Debug

            return JsonResponse({
                'success': True,
                'message': 'Orden creada exitosamente.',
                'order_id': order.id,
                'transaction_id': transaction_id
            })

        except json.JSONDecodeError as e:
            print(f"DEBUG - Error JSON: {e}")  # Debug
            print(f"DEBUG - Request.body problemático: {request.body}")  # Debug
            return JsonResponse({'error': 'Datos JSON inválidos'}, status=400)
        except Exception as e:
            print(f"DEBUG - Error general: {e}")  # Debug
            import traceback
            print(f"DEBUG - Traceback completo:")
            traceback.print_exc()
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Método no permitido'}, status=405)

@csrf_exempt
def test_order_creation(request):
    """Vista de prueba para debug"""
    if request.method == 'POST':
        # Datos de prueba simulando un carrito real
        test_cart = [
            {
                "id": 1,
                "name": "Test Product",
                "price": 25.0,
                "quantity": 1,
                "description": "Test description"
            }
        ]
        
        print(f"TEST DEBUG - Carrito de prueba: {test_cart}")
        
        # Simular la llamada igual que confirm_purchase
        try:
            user = request.user if request.user.is_authenticated else None
            order = Order.objects.create(user=user, total=0, status='completed')
            total = 0

            for item in test_cart:
                try:
                    product_id = item.get('id')
                    print(f"TEST DEBUG - Buscando producto ID: {product_id}")
                    product = Product.objects.get(id=product_id)
                    print(f"TEST DEBUG - Producto encontrado: {product.name}")
                    
                    quantity = int(item.get('quantity', 1))
                    price = float(item.get('price', product.price))
                    item_total = price * quantity
                    total += item_total
                    
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=quantity,
                        price=price
                    )
                    
                except Product.DoesNotExist:
                    print(f"TEST DEBUG - Producto no encontrado: {item}")
                    continue
            
            order.total = total
            order.save()
            
            print(f"TEST DEBUG - Orden creada: ID={order.id}, Total={total}")
            
            return JsonResponse({
                'success': True,
                'order_id': order.id,
                'total': float(total)
            })
            
        except Exception as e:
            print(f"TEST DEBUG - Error: {e}")
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)


