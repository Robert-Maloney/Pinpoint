from django.urls import re_path
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from .consumers import ChatConsumer

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<event_id>\w+)/$', ChatConsumer.as_asgi()),
]

# application = ProtocolTypeRouter({
#     "websocket": AuthMiddlewareStack(
#         URLRouter(websocket_urlpatterns)
#     ),
# })

# import logging
# logger = logging.getLogger(__name__)
# logger.info("WebSocket routing loaded")
