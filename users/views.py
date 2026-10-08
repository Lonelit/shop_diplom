from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q, Count
from django.conf import settings
from django.contrib.auth import login, authenticate, logout, get_user_model
from shop.models import Goods
from .forms import CustomUserCreationForm, CustomUserUpdateForm
from django.contrib import messages

User = get_user_model()


def register_view(request):
    """ Регистрация пользователя """
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('shop:goods_list')
    else:
        form = CustomUserCreationForm()

    return render(request, 'users/register.html', context={"form": form})


def log_in_view(request):
    """ Авторизация пользователя """
    if request.method == "POST":
        # ИСПРАВЛЕНО: Передаем POST-данные только при отправке формы
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                # ИСПРАВЛЕНО: Безопасно берем LOGIN_REDIRECT_URL прямо из settings
                url = request.GET.get('next', settings.LOGIN_REDIRECT_URL)
                return redirect(url)
    else:
        # Если запрос GET — показываем чистую форму
        form = AuthenticationForm()

    return render(request, template_name='users/login.html', context={'form': form})


@login_required
def log_out_view(request):
    """ Выход из системы """
    logout(request)
    return redirect('shop:main')


@login_required
def user_detail_view(request, pk):
    """ Просмотр профиля пользователя """
    user = get_object_or_404(User, pk=pk)
    goods = (
        Goods.objects.select_related('seller', 'category')
        .prefetch_related('likes')
        .filter(seller=user)
        .annotate(likes_count=Count('likes'))
        .order_by('-created_at')
    )

    context = {
        'is_me': request.user == user,
        'profile_user': user,
        'title': 'Информация о профиле',
        'goods': goods,
    }
    return render(request, template_name='users/profile.html', context=context)

@login_required
def profile_edit_view(request):
    """Редактирование профиля текущего пользователя"""
    if request.method == "POST":
        # Передаем вашу форму CustomUserUpdateForm
        form = CustomUserUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлен!')
            return redirect('users:profile', pk=request.user.pk)
    else:
        form = CustomUserUpdateForm(instance=request.user)

    return render(request, 'users/profile_edit.html', context={'form': form, 'title': 'Настройки профиля'})