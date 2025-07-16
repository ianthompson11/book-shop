from django.contrib import admin
from .models import Category, Product

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at')
    search_fields = ('name',)
    list_filter = ('created_at',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'category', 'product_type', 'price', 'stock', 'created_at')
    list_filter = ('category', 'product_type', 'created_at')
    search_fields = ('name', 'author', 'isbn')
    list_editable = ('price', 'stock')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Información General', {
            'fields': ('name', 'description', 'author', 'isbn')
        }),
        ('Clasificación', {
            'fields': ('category', 'product_type')
        }),
        ('Precio y Stock', {
            'fields': ('price', 'stock')
        }),
        ('Imagen', {
            'fields': ('image',)
        }),
        ('Fechas', {
         'fields': ('publication_date', 'created_at', 'updated_at'),
         'classes': ('collapse',)
        }),

    )
