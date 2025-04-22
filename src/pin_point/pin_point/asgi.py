"""
ASGI config for pin_point project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/
"""

from django.core.asgi import get_asgi_application
from channels.routing import URLRouter, ProtocolTypeRouter
from channels.auth import AuthMiddlewareStack
from channels.sessions import SessionMiddlewareStack
import map_features.routing

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": SessionMiddlewareStack(  # Ensures Django sessions are available
        AuthMiddlewareStack(  # Ensures user authentication is passed
            URLRouter(
                map_features.routing.websocket_urlpatterns
            )
        )
    ),
})
