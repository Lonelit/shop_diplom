from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    """
    Форма регистрации.
    Наследуемся от UserCreationForm, чтобы не писать проверку пароля вручную.
    """
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'phone', 'city', 'avatar')

class CustomUserUpdateForm(forms.ModelForm):
    """
    Форма редактирования профиля (без смены пароля).
    """
    class Meta:
        model = CustomUser
        # Эти поля будут доступны пользователю для изменения в настройках:
        fields = ('username', 'email', 'phone', 'city', 'avatar')