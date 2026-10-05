from django.db import models
from django.conf import settings
from django.urls import reverse
from django.core.validators import MinValueValidator
from decimal import Decimal


class Category(models.Model):
    """
    категория
    связь один ко многим
    """
    name = models.CharField('название', max_length=80, unique=True)
    slug = models.SlugField('slug', max_length=90, unique=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name

class Goods(models.Model):
    """
    Товары. Изображения храним в модели магаза (ограничение - 3 картинки)
    """
    objects = models.Manager()
    title = models.CharField('название', max_length=200)
    text = models.TextField('описание')
    price = models.DecimalField(
        'цена',
        max_digits=10,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='goods',
        verbose_name='продавец'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='goods',
        verbose_name='категория'
    )

    image1 = models.ImageField('изображение 1', upload_to='goods/', blank=True, null=True)
    image2 = models.ImageField('изображение 2', upload_to='goods/', blank=True, null=True)
    image3 = models.ImageField('изображение 3', upload_to='goods/', blank=True, null=True)
    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='liked_goods',
        verbose_name='лайки'
    )
    created_at = models.DateTimeField('создано', auto_now_add=True)
    updated_at = models.DateTimeField('обновлено', auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.title

    def like_count(self):
        return self.likes.count()

    def get_absolute_url(self):
        return reverse('shop:goods_detail', kwargs={'pk': self.pk})