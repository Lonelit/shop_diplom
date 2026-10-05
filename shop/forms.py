from django import forms
from .models import Goods

class GoodsForm(forms.ModelForm):
    """
    Форма создания и редактирования товаров
    """
    class Meta:
        model = Goods
        fields = ('title', 'text', 'price', 'category', 'image1', 'image2', 'image3')
        widgets = {
            'text': forms.Textarea(attrs={'rows':8}),
            'price': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control', 'placeholder': '0.00'}),
        }
