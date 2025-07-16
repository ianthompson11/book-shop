"""
URL configuration for mysite project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Ruta del panel de administración
    path('admin/', admin.site.urls),
    
    # Rutas de autenticación incluidas (login, logout, etc.)
    path("accounts/", include("django.contrib.auth.urls")),
    
    # Include URLs from productos app
    path('productos/', include('productos.urls')),
    
    # Include URLs from store app
    path('', include('store.urls')),
]

# CONFIGURACIÓN PARA SERVIR ARCHIVOS DE IMAGEN (MEDIA) EN MODO DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    path('', include('store.urls')),
]

# CONFIGURACIÓN PARA SERVIR ARCHIVOS DE IMAGEN (MEDIA) EN MODO DEBUG
# Permite acceder a imágenes subidas desde el admin, como http://localhost:8000/media/products/imagen.jpg
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

