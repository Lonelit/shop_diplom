from django.urls import path, include
from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.goods_list, name='main'),
    path('goods/me/', views.my_goods, name='my_goods'),
    path('goods/create/', views.goods_create, name='goods_create'),
    path('goods/<int:pk>/', views.goods_detail, name='goods_detail'),
    path('goods/<int:pk>/edit/', views.goods_update, name='goods_update'),
    path('goods/<int:pk>/delete/', views.goods_delete, name='goods_delete'),
    path('goods/', views.goods_list, name='goods_list'),
    path('goods/<int:pk>/like/', views.goods_like, name='goods_like'),

    path('users/<int:user_id>/goods/', views.user_goods, name='user_goods'),


]