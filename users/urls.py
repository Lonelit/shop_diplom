from django.urls import path
from . import views
#обращаемся к конкретному приложению, в нашем случае users
app_name = 'users'

urlpatterns = [
    path('register/', views.register_view, name = 'register'),
    path('login/', views.log_in_view, name = 'login'),
    path('logout/', views.log_out_view, name = 'logout'),
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),
    path('profile/<int:pk>/', views.user_detail_view, name = 'profile'),

]