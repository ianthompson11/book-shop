from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q, Avg
from .models import Product, Category, Rating
from .forms import ProductForm, RatingForm

# VISTAS DE PRODUCTOS
def productos_view(request):
    # Obtener todas las categorías
    categories = Category.objects.all()

    # Obtener productos con promedio de calificación
    # Ordenar por promedio de calificación descendente (mejor calificados primero)
    products = Product.objects.select_related('category').annotate(avg_rating=Avg('ratings__score')).order_by('-avg_rating')[:10]

    context = {
        'categories': categories,
        'products': products,
    }
    return render(request, 'productos/productos.html', context)


# VISTAS PÚBLICAS
def product_list(request):
   # Corregido: select_related para evitar N+1 queries
   products = Product.objects.select_related('category').annotate(avg_rating=Avg('ratings__score'))
   categories = Category.objects.all()
   
   # Filtros y búsqueda
   category_id = request.GET.get('category')
   if category_id:
       products = products.filter(category_id=category_id)
   
   product_type = request.GET.get('type')
   if product_type:
       products = products.filter(product_type=product_type)
   
   search = request.GET.get('search', '')
   if search:
       products = products.filter(
           Q(name__icontains=search) | Q(author__icontains=search)
       )
   
   context = {
       'products': products,
       'categories': categories,
       'selected_category': category_id,
       'selected_type': product_type,
       'search_query': search,
   }
   return render(request, 'productos/product_list.html', context)


def product_detail(request, pk):
    product = get_object_or_404(Product.objects.select_related('category').annotate(avg_rating=Avg('ratings__score')), pk=pk)
    ratings = product.ratings.select_related('user')

    if request.user.is_authenticated:
        existing_rating = Rating.objects.filter(product=product, user=request.user).first()
        if request.method == 'POST':
            form = RatingForm(request.POST, instance=existing_rating)
            if form.is_valid():
                rating = form.save(commit=False)
                rating.user = request.user
                rating.product = product
                rating.save()
                messages.success(request, 'Gracias por tu calificación.')
                return redirect('product_detail', pk=pk)
        else:
            form = RatingForm(instance=existing_rating)
    else:
        form = None

    return render(request, 'productos/product_detail.html', {
        'product': product,
        'ratings': ratings,
        'form': form
    })

# VISTAS ADMIN (sin restricciones por ahora)
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)  # <--- IMPORTANTE

            # Lógica de selección de fuente de imagen
            image_source = request.POST.get('image_source')
            image_url = form.cleaned_data.get('image_url')
            image_file = request.FILES.get('image')

            if image_source == 'url' and image_url:
                product.image = None  # No se guarda imagen subida
            elif image_source == 'file' and image_file:
                product.image_url = ''  # Limpiar URL si se sube imagen
            elif image_source == 'url' and not image_url and image_file:
                # Fallback: si URL vacía pero hay archivo
                product.image_url = ''
            else:
                # Si no se seleccionó nada útil, limpiar ambos
                product.image = None
                product.image_url = ''

            product.save()
            messages.success(request, 'Producto creado exitosamente.')
            return redirect('product_list')
    else:
        form = ProductForm()

    return render(request, 'productos/product_form.html', {
        'form': form,
        'title': 'Crear Producto'
    })


def product_update(request, pk):
   # Corregido: select_related para evitar N+1 queries
   product = get_object_or_404(Product.objects.select_related('category'), pk=pk)
   
   if request.method == 'POST':
       form = ProductForm(request.POST, request.FILES, instance=product)
       if form.is_valid():
            product = form.save(commit=False)

            image_source = request.POST.get('image_source')
            image_url = form.cleaned_data.get('image_url')
            image_file = request.FILES.get('image')

            if image_source == 'url' and image_url:
                product.image = None
            elif image_source == 'file' and image_file:
                product.image_url = ''
            elif image_source == 'url' and not image_url and image_file:
                product.image_url = ''
            else:
                product.image = None
                product.image_url = ''

            product.save()
            messages.success(request, 'Producto actualizado exitosamente.')
            return redirect('product_detail', pk=product.pk)
   else:
       form = ProductForm(instance=product)
   
   return render(request, 'productos/product_form.html', {
       'form': form,
       'title': 'Editar Producto',
       'product': product
   })

def product_delete(request, pk):
   # Corregido: select_related para evitar N+1 queries
   product = get_object_or_404(Product.objects.select_related('category'), pk=pk)
   
   if request.method == 'POST':
       product.delete()
       messages.success(request, 'Producto eliminado exitosamente.')
       return redirect('product_list')
   
   return render(request, 'productos/product_confirm_delete.html', {'product': product})