from django.shortcuts import render
from django.shortcuts import render, redirect
from .paypal_views import create_order, capture_order #Importa del archivo paypal_views.py sus funciones para no sobrepoblar views
from django.utils.cache import patch_cache_control #para evitar que recargue el sitio payments desde la cache
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
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
def marcar_compra_completada(request):
    """
    Vista para marcar una compra como completada después del pago exitoso.
    Esta vista permite limpiar el carrito del lado del cliente.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            compra_confirmada = data.get('compraConfirmada', False)
            transaction_id = data.get('transaction_id', '')
            status = data.get('status', '')
            
            if compra_confirmada:
                # Aquí se pueden realizar acciones adicionales como:
                # - Enviar emails de confirmación
                # - Actualizar estadísticas
                # - Registrar en logs
                # - etc.
                
                return JsonResponse({
                    'success': True, 
                    'message': 'Compra confirmada exitosamente',
                    'clear_cart': True  # Indica al frontend que debe limpiar el carrito
                })
            else:
                return JsonResponse({'success': False, 'message': 'Compra no confirmada'}, status=400)
                
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)


