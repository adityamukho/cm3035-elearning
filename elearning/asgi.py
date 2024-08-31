import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from django.apps import apps

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'elearning.settings')

django_asgi_app = get_asgi_application()

def get_channelsmiddleware_application():
    from channels.auth import AuthMiddlewareStack
    import chat.routing
    return ProtocolTypeRouter({
        "http": django_asgi_app,
        "websocket": AuthMiddlewareStack(
            URLRouter(
                chat.routing.websocket_urlpatterns
            )
        ),
    })

application = get_channelsmiddleware_application()
