from django import forms
from .models import Goods

class GoodsForm(forms.ModelForm):
    """
    Форма создания и редактирования товаров
    """
    class Meta:
        model = Goods
        fields = ('title', 'text', 'category', 'image1', 'image2', 'image3')
        widgets = {
            'text': forms.Textarea(attrs={'rows':8}),
            'tags': forms.CheckboxSelectMultiple(),
        }
