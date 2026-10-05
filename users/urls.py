from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
# from .views import * перечень функций *, а . импортирует все функции сразу

#обращаемся к конкретному приложению, в нашем случае users
app_name = 'users'

urlpatterns = [
    path('register/', views.register_view, name = 'register'),

    # path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name = 'login'),
    path('login/', views.log_in_view, name = 'login'),
    # path('logout/', auth_views.LogoutView.as_view(), name = 'logout'),
    path('logout/', views.log_out_view, name = 'logout'),

    path('profile/<int:pk>/', views.user_detail_view, name = 'profile'),


]