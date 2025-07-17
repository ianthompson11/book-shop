from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'author', 'category', 'product_type', 'price', 'stock', 'description', 'image','image_url', 'isbn','publication_date']
        common_class = 'w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500'

        widgets = {
            'name': forms.TextInput(attrs={'class': common_class}),
            'author': forms.TextInput(attrs={'class': common_class}),
            'category': forms.Select(attrs={'class': common_class}),
            'product_type': forms.Select(attrs={'class': common_class}),
            'price': forms.NumberInput(attrs={'class': common_class, 'step': '0.01'}),
            'stock': forms.NumberInput(attrs={'class': common_class}),
            'description': forms.Textarea(attrs={'class': common_class, 'rows': 4}),
            'image': forms.FileInput(attrs={'class': common_class}),
            'image_url': forms.URLInput(attrs={'class': common_class}),
            'isbn': forms.TextInput(attrs={'class': common_class}),
            'publication_date': forms.DateInput(attrs={'class': common_class, 'type': 'date'}),
        }
    def clean_isbn(self):
            isbn = self.cleaned_data.get('isbn')
            if not isbn.isdigit() or len(isbn) != 13:
                raise forms.ValidationError("El ISBN debe tener exactamente 13 dígitos numéricos.")

            # Verifica si ya existe otro producto con el mismo ISBN
            if Product.objects.filter(isbn=isbn).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError("Este ISBN ya está registrado para otro libro.")
            return isbn

from .models import Rating
class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['score', 'comment']
        widgets = {
            'score': forms.Select(
                choices=[(i, f"{i} ⭐") for i in range(1, 6)],
                attrs={'class': 'form-control'}
            ),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
