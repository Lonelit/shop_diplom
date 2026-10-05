from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    """
    Расширенная модель пользователя
    AbstractUser уже содержит username, first_name, last_name, e-mail, password, is_stuff...
    мы добавляем свои поля: телефон, город, аватар
    """
    phone = models.CharField(
        'телефон',
        max_length=20,
        blank=True,
        help_text="Можно оставить пустым"
    )
    city = models.CharField(
        'город',
        max_length=100,
        blank=True
    )
    avatar = models.ImageField(
        'аватар',
        upload_to='avatars/',
        blank=True,
        null=True
    )
    def __str__(self):
        return self.username
