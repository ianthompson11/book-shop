# payments/views.py
import os
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from paypalserversdk.http.auth.o_auth_2 import ClientCredentialsAuthCredentials
from paypalserversdk.paypal_serversdk_client import PaypalServersdkClient
from paypalserversdk.controllers.orders_controller import OrdersController
from paypalserversdk.controllers.payments_controller import PaymentsController
from paypalserversdk.models.order_request import OrderRequest
from paypalserversdk.models.checkout_payment_intent import CheckoutPaymentIntent
from paypalserversdk.models.purchase_unit_request import PurchaseUnitRequest
from paypalserversdk.models.amount_with_breakdown import AmountWithBreakdown
from paypalserversdk.models.amount_breakdown import AmountBreakdown
from paypalserversdk.models.money import Money
from paypalserversdk.models.item import Item
from paypalserversdk.models.item_category import ItemCategory
from paypalserversdk.logging.configuration.api_logging_configuration import (
    LoggingConfiguration,
    RequestLoggingConfiguration,
    ResponseLoggingConfiguration,
)
from paypalserversdk.api_helper import ApiHelper

paypal_client = PaypalServersdkClient(
    client_credentials_auth_credentials=ClientCredentialsAuthCredentials(
        o_auth_client_id=os.getenv("PAYPAL_CLIENT_ID"),
        o_auth_client_secret=os.getenv("PAYPAL_CLIENT_SECRET"),
    ),
    logging_configuration=LoggingConfiguration(
        request_logging_config=RequestLoggingConfiguration(log_headers=True, log_body=True),
        response_logging_config=ResponseLoggingConfiguration(log_headers=True, log_body=True),
        mask_sensitive_headers=False,
    ),
)

orders_controller = paypal_client.orders
payments_controller = paypal_client.payments

def index(request):
    return render(request, "payments/index.html", {
        "PAYPAL_CLIENT_ID": os.getenv("PAYPAL_CLIENT_ID")
    })

@csrf_exempt
def create_order(request):
    if request.method == "POST":
        import json
        body = json.loads(request.body)
        cart = body.get("cart", [])  # no usado en este ejemplo
        order = orders_controller.create_order({
            "body": OrderRequest(
                intent=CheckoutPaymentIntent.CAPTURE,
                purchase_units=[
                    PurchaseUnitRequest(
                        amount=AmountWithBreakdown(
                            currency_code="USD",
                            value="100", #Aqui se le esta indicando cuantoo cobrar
                            breakdown=AmountBreakdown(
                                item_total=Money(currency_code="USD", value="100")
                            ),
                        ),
                        items=[
                            Item(
                                name="T-Shirt",
                                unit_amount=Money(currency_code="USD", value="100"),
                                quantity="1",
                                description="Super Fresh Shirt",
                                sku="sku01",
                                category=ItemCategory.PHYSICAL_GOODS,
                            )
                        ],
                    )
                ]
            )
        })

        return HttpResponse(
        ApiHelper.json_serialize(order.body),
        content_type="application/json",
        status=200
        )

  



@csrf_exempt
def capture_order(request, order_id):
    if request.method == "POST":
        order = orders_controller.capture_order({
            "id": order_id,
            "prefer": "return=representation"
        })
        return HttpResponse(
        ApiHelper.json_serialize(order.body),
        content_type="application/json",
        status=200
        )

