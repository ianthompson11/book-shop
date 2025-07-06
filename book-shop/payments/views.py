from django.shortcuts import render
from .paypal_views import create_order, capture_order #Importa del archivo paypal_views.py sus funciones para no sobrepoblar views
import os
from dotenv import load_dotenv # libreria para cargar la variable del archivo .env #payments

load_dotenv() # comando para cargar la variable del archivo .env #payments
def index(request): 
    return render(request, "payments/index.html", {
        "PAYPAL_CLIENT_ID": os.getenv("PAYPAL_CLIENT_ID")  #toma el PAYPAL_CLIENT_ID del env guardado en el terminal
    })
