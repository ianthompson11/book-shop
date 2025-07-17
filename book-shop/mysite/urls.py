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
from django.views.generic import TemplateView
from django.views.generic import RedirectView
from django.contrib.auth.decorators import login_required
from usuarios.views import PasswordSelfResetView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    path('', include('usuarios.urls')),  # Comenta esto temporalmente
    path(
        'accounts/password/manual-reset/',
        PasswordSelfResetView.as_view(),
        name='password_self_reset'
    ),
    path('user/panel/', TemplateView.as_view(template_name='user_panel.html'), name='user_panel'),
    path('', RedirectView.as_view(url='/accounts/login/', permanent=False)),  # Redirige a login como punto de entrada
    path('home/', login_required(TemplateView.as_view(template_name='home.html')), name='home'),  # Página principal protegida
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),   # URLs de django-allauth
    path('productos/', include('productos.urls')), # Include the URLs from the productos app
    path('', include('store.urls')), # Include the URLs from the store app
    path('', include('payments.urls')), # payments
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)