from django.contrib import admin
from .models import Category, Goods


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug':('name',)}

@admin.register(Goods)
class ShopAdmin(admin.ModelAdmin):
    list_display = ('title', 'seller', 'category', 'price', 'created_at', 'like_count')
    list_filter = ( 'created_at','category', 'seller')
    search_fields = ('title','seller__username', 'category__name')
    filter_horizontal = ('likes',)