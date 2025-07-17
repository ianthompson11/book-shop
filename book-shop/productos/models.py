from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator # Validación para ISBN

# Modelo para la categoría de libros
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Nombre")
    description = models.TextField(blank=True, verbose_name="Descripción")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"

    def __str__(self):
        return self.name

# Modelo para los productos (libros)
class Product(models.Model):
    PRODUCT_TYPES = [
        ('physical', 'Libro Físico'),
        ('ebook', 'Libro Digital'),
    ]

    name = models.CharField(max_length=200, verbose_name="Nombre")
    description = models.TextField(verbose_name="Descripción")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio")
    product_type = models.CharField(
        max_length=10,
        choices=PRODUCT_TYPES,
        default='physical',
        verbose_name="Tipo de producto"
    )
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="Categoría")
    stock = models.PositiveIntegerField(default=0, verbose_name="Stock")
    image = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name="Imagen")
    image_url = models.URLField(blank=True, null=True)
    author = models.CharField(max_length=100, verbose_name="Autor")
    isbn = models.CharField(max_length=13,unique=True,validators=[RegexValidator(regex='^\d{13}$', message='El ISBN debe tener exactamente 13 dígitos.')],verbose_name="ISBN")
    publication_date = models.DateField(verbose_name="Fecha de publicación")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")
    
    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"

    def __str__(self):
        tipo = 'Digital' if self.product_type == 'ebook' else 'Físico'
        return f"{self.name} ({tipo})"

    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'pk': self.pk})

    def clean(self):
        # Validación para asegurar que solo los libros físicos tengan stock > 0
        if self.product_type == 'ebook' and self.stock > 0:
            raise ValidationError({'stock': "Los libros digitales no deben tener stock."})
        if self.product_type == 'physical' and self.stock == 0:
            raise ValidationError({'stock': "Los libros físicos deben tener stock mayor a cero."})

# Modelo para calificaciones de libros
class Rating(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='ratings', verbose_name="Libro")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuario")  # Quién hizo la calificación
    score = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1, "La puntuación mínima es 1."),
            MaxValueValidator(5, "La puntuación máxima es 5.")
        ],
        verbose_name="Puntuación"
    )
    comment = models.TextField(blank=True, verbose_name="Comentario")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de calificación")

    class Meta:
        verbose_name = "Calificación"
        verbose_name_plural = "Calificaciones"
        unique_together = ('product', 'user')  # Un usuario no puede calificar el mismo libro más de una vez

    def __str__(self):
        return f"{self.product.name} - {self.score}⭐ por {self.user.username}"
