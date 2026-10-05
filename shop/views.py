from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count

from shop.forms import GoodsForm
from shop.models import Goods, Category

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
    """
    Главная страниуа со списком товаров
    -поиск по заголовку и тексту
    -фильтрация по автору, категории
    сортировка по дате, заголовку и кол-ву лайков

    """
    # получаем все посты из БД
    # select_related (поля ForeignKey)
    # prefetch_related (поля ManytoMany)
    goods = Goods.objects.select_related('seller', 'category').prefetch_related('likes')


    # получение из форм HTML запроса в GET-запросе
    query = request.GET.get('q', '').strip()
    seller_id = request.GET.get('seller','')
    category_id = request.GET.get('category','')
    sort = request.GET.get('sort','-created_at')

    if query:
        goods = goods.filter(Q(title__icontains=query) | Q(text__icontains=query))
        # __icontains регистронезависимое содержимое

    if seller_id:
        goods = goods.filter(author_id=seller_id)

    if category_id:
        goods = goods.filter(category_id=category_id)

    # annotate добавляет каждому посту вычесленное поле likes.count
    # по нему можно сортировать список
    goods = goods.annotate(likes_count=Count('likes'))

    allowed_sort_fields = {
        '-created_at': '-created_at',
        'created_at': 'created_at',
        'title': 'title',
        '-title': '-title',
        '-likes': '-likes_count',
        'likes': 'likes_count',
    }
    goods = goods.order_by(allowed_sort_fields.get(sort), '-created_at')

    context = {
        'goods': goods,
        'query': query,
        'categories': Category.objects.all(),
        'sellers': get_user_model().objects.all().order_by('username'),
        'selected_seller':seller_id,
        'selected_category':category_id,
        'selected_sort':sort,
        'page_heading': 'Товары',
        'page_description': 'Выберете товары, ищите по тексту, фильтруйте по продавцу и категории'
    }
    return render(request, template_name='shop/goods_list.html', context=context)

def user_goods(request, user_id):

    """
    просмотр товаров любого пользователя
    user_id приходит из адреса страницы
    """
    seller = get_object_or_404(get_user_model(), pk=user_id)
    goods = (
        Goods.objects.select_related('seller', 'category')
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
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user:
        messages.error(request, "Можно редактировать только свои посты")
        return redirect(post)
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, "Пост обновлен!")
            return redirect(post)
    else:
        form = PostForm(instance=post)
    return render(request, template_name='blog/post_form.html', context={'form': form})

@login_required
def post_delete(request, pk):
    """
    Пользователь может удалить только свой пост
    админ(is_staff = True) может удалить любой пост
    """
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user and not request.user.is_staff:
        messages.error(request, "Удалять можно только свои посты")
        return redirect(post)
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Пост удален')
        return redirect('blog:post_list')
    return render(request, 'blog/post_confirm_delete.html', context={'post': post})


@login_required
def post_like(request, pk):
    """ поставить или убрать лайк"""
    post = get_object_or_404(Post, pk=pk)
    if request.user in post.likes.all():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)

    return redirect(request.META.get('HTTP_REFERER', post.get_absolute_url()))