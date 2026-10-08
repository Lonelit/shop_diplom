from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count

from shop.forms import GoodsForm
from shop.models import Goods, Category

from django.views.decorators.http import require_POST
from .cart import Cart

@login_required
def goods_create(request):
    if request.method =="POST":
        form = GoodsForm(request.POST, request.FILES)
        if form.is_valid():
            goods = form.save(commit=False)
            goods.seller = request.user
            goods.save()
            form.save_m2m()
            messages.success(request, 'товар создан!')
            return redirect(goods.get_absolute_url())
    else:
        form = GoodsForm()
    return render(request,
                 'shop/goods_form.html',
                  context={'form': form, 'title': 'Новый товар'})

def goods_detail(request, pk):
    goods = get_object_or_404(
        Goods.objects.select_related('seller', 'category').prefetch_related('likes'),
        pk=pk,
    )
    return render(request, 'shop/goods_detail.html', context={'goods': goods})


def goods_list(request):
    """ Главная страница со списком товаров с фильтром по цене """
    goods = Goods.objects.select_related('seller', 'category').prefetch_related('likes')

    query = request.GET.get('q', '').strip()
    seller_id = request.GET.get('seller', '')
    category_id = request.GET.get('category', '')
    sort = request.GET.get('sort', '-created_at')

    # НОВОЕ: Получаем диапазон цен из GET-запроса
    price_min = request.GET.get('price_min', '')
    price_max = request.GET.get('price_max', '')

    if query:
        goods = goods.filter(Q(title__icontains=query) | Q(text__icontains=query))

    if seller_id:
        goods = goods.filter(seller_id=seller_id)

    if category_id:
        goods = goods.filter(category_id=category_id)

    # НОВОЕ: Фильтрация по минимальной и максимальной цене
    if price_min:
        goods = goods.filter(price__gte=price_min)  # gte = больше или равно
    if price_max:
        goods = goods.filter(price__lte=price_max)  # lte = меньше или равно

    goods = goods.annotate(likes_count=Count('likes'))

    allowed_sort_fields = {
        '-created_at': '-created_at',
        'created_at': 'created_at',
        'title': 'title',
        '-title': '-title',
        '-likes': '-likes_count',
        'likes': 'likes_count',
        'price': 'price',  # НОВОЕ: сортировка по возрастанию цены
        '-price': '-price',  # НОВОЕ: сортировка по убыванию цены
    }
    goods = goods.order_by(allowed_sort_fields.get(sort, '-created_at'), '-created_at')

    context = {
        'goods': goods,
        'query': query,
        'categories': Category.objects.all(),
        'sellers': get_user_model().objects.all().order_by('username'),
        'selected_seller': seller_id,
        'selected_category': category_id,
        'selected_sort': sort,
        # НОВОЕ: Передаем значения цен обратно в форму, чтобы они не сбрасывались
        'price_min': price_min,
        'price_max': price_max,
        'page_heading': 'Товары',
        'page_description': 'Выберите товары, ищите по тексту, фильтруйте по цене, продавцу и категории'
    }
    return render(request, template_name='shop/goods_list.html', context=context)


def user_goods(request, user_id):

    """
    просмотр товаров любого пользователя
    user_id приходит из адреса страницы
    """
    seller = get_object_or_404(get_user_model(), pk=user_id)
    goods = (
        Goods.objects.select_related('seller', 'category', 'price')
        .prefetch_related('likes')
        .filter(seller=seller)
        .annotate(likes_count=Count('likes'))
        .order_by('-created_at')
    )
    context = {
        'goods': goods,
        'hide_filters': True,
        'page_heading': f'Товары продавца {seller.username}',
        'page_description': 'Товары продавца'
    }
    return render(request, template_name='shop/goods_list.html', context=context)

@login_required
def my_goods(request):

    """
    просмотр товаров текущего пользователя
    """

    goods = (
        Goods.objects.select_related('seller', 'category')
        .prefetch_related('likes')
        .filter(seller=request.user)
        .annotate(likes_count=Count('likes'))
        .order_by('-created_at')
    )
    context = {
        'goods': goods,
        'hide_filters': True,
        'page_heading': 'Мои товары',
        'page_description': 'Все опубликованные мной товары'
    }
    return render(request, template_name='shop/goods_list.html', context=context)

@login_required
def goods_update(request, pk):
    """
    редактировать можно только свои товары

    """
    goods = get_object_or_404(Goods, pk=pk)
    if goods.seller != request.user:
        messages.error(request, "Можно редактировать только свои товары")
        return redirect(goods)
    if request.method == 'POST':
        form = GoodsForm(request.POST, request.FILES, instance=goods)
        if form.is_valid():
            form.save()
            messages.success(request, "Товар обновлен!")
            return redirect(goods)
    else:
        form = GoodsForm(instance=goods)
    return render(request, template_name='shop/goods_form.html', context={'form': form})

@login_required
def goods_delete(request, pk):
    """
    Пользователь может удалить только свой товар
    админ(is_staff = True) может удалить любой товар
    """
    goods = get_object_or_404(Goods, pk=pk)
    if goods.seller != request.user and not request.user.is_staff:
        messages.error(request, "Удалять можно только свои товары")
        return redirect(goods)
    if request.method == 'POST':
        goods.delete()
        messages.success(request, 'Товар удален')
        return redirect('shop:goods_list')
    return render(request, 'shop/goods_confirm_delete.html', context={'goods': goods})


@login_required
def goods_like(request, pk):
    """ поставить или убрать лайк"""
    goods = get_object_or_404(Goods, pk=pk)
    if request.user in goods.likes.all():
        goods.likes.remove(request.user)
    else:
        goods.likes.add(request.user)

    return redirect(request.META.get('HTTP_REFERER', goods.get_absolute_url()))

@require_POST
def cart_add(request, goods_id):
    """ Обработчик добавления товара в корзину """
    cart = Cart(request)
    goods = get_object_or_404(Goods, id=goods_id)
    # По умолчанию добавляем 1 штуку.
    # При желании количество можно забирать из request.POST['quantity']
    cart.add(goods=goods, quantity=1)
    messages.success(request, f'Товар "{goods.title}" добавлен в корзину!')
    return redirect(request.META.get('HTTP_REFERER', 'shop:goods_list'))

def cart_remove(request, goods_id):
    """ Обработчик удаления товара из корзины """
    cart = Cart(request)
    goods = get_object_or_404(Goods, id=goods_id)
    cart.remove(goods)
    messages.warning(request, f'Товар "{goods.title}" удален из корзины.')
    return redirect('shop:cart_detail')

def cart_detail(request):
    """ Страница просмотра содержимого корзины """
    cart = Cart(request)
    return render(request, 'shop/cart_detail.html', context={'cart': cart})