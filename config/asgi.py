import os
from django.core.asgi import get_asgi_application

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import shop.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = ProtocolTypeRouter({
    # Стандартный HTTP-протокол (наши обычные views)
    "http": get_asgi_application(),

    # WebSocket-протокол (наш реального времени чат)
    "websocket": AuthMiddlewareStack(
        URLRouter(
            shop.routing.websocket_urlpatterns
        )
    ),
})
