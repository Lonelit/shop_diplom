from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    # 1. Главная страница приложения
    path('', views.goods_list, name='main'),

    # 2. Статические текстовые маршруты для товаров
    path('goods/', views.goods_list, name='goods_list'),
    path('goods/me/', views.my_goods, name='my_goods'),
    path('goods/create/', views.goods_create, name='goods_create'),

    # 3. Динамические маршруты по ID товара
    path('goods/<int:pk>/', views.goods_detail, name='goods_detail'),
    path('goods/<int:pk>/edit/', views.goods_update, name='goods_update'),
    path('goods/<int:pk>/delete/', views.goods_delete, name='goods_delete'),
    path('goods/<int:pk>/like/', views.goods_like, name='goods_like'),

    # 4. Профиль товаров конкретного пользователя
    path('users/<int:user_id>/goods/', views.user_goods, name='user_goods'),

    # 5. Маршруты для корзины
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:goods_id>/', views.cart_add, name='cart_add'),
    path('cart/remove/<int:goods_id>/', views.cart_remove, name='cart_remove'),
]