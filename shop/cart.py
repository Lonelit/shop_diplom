from decimal import Decimal
from django.conf import settings
from shop.models import Goods


class Cart:
    def __init__(self, request):
        """ Инициализация корзины из сессии запроса """
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            # Если корзины нет в сессии, создаем пустую
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, goods, quantity=1, override_quantity=False):
        """ Добавить товар в корзину или обновить его количество """
        goods_id = str(goods.id)
        if goods_id not in self.cart:
            self.cart[goods_id] = {
                'quantity': 0,
                'price': str(goods.price)
            }

        if override_quantity:
            self.cart[goods_id]['quantity'] = quantity
        else:
            self.cart[goods_id]['quantity'] += quantity
        self.save()

    def save(self):
        """ Отметить сессию как измененную, чтобы она сохранилась в БД/куках """
        self.session.modified = True

    def remove(self, goods):
        """ Удаление товара из корзины """
        goods_id = str(goods.id)
        if goods_id in self.cart:
            del self.cart[goods_id]
            self.save()

    def __iter__(self):
        """ Перебор элементов в корзине и получение товаров из базы данных """
        goods_ids = self.cart.keys()
        # Получаем объекты товаров из БД
        goods_objects = Goods.objects.filter(id__in=goods_ids)

        cart = self.cart.copy()
        for goods in goods_objects:
            cart[str(goods.id)]['goods'] = goods

        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        """ Подсчет общего количества товаров в корзине """
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        """ Подсчет общей стоимости всех товаров в корзине """
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def clear(self):
        """ Очистка корзины """
        del self.session[settings.CART_SESSION_ID]
        self.save()