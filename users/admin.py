from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительная информация', {'fields': ('phone', 'city', 'avatar')}),
    )
    list_display = ('username', 'email', 'phone', 'city', 'is_staff')
