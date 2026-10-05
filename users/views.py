from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q, Count
from django.conf import settings
from django.contrib.auth import login, authenticate, logout, get_user_model
from shop.models import Goods
from .forms import CustomUserCreationForm

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
        # ИСПРАВЛЕНО: Компактное и понятное присвоение флага «Это мой профиль»
        'is_me': request.user == user,
        'user': user,
        'title': 'Информация о профиле',
        'goods': goods,
    }
    return render(request, template_name='users/profile.html', context=context)
