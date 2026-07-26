"""
ASGI config for config project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

from channels.routing import ProtocolTypeRouter
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

django_asgi_app = get_asgi_application()

from devops.realtime.middleware import JWTWebSocketMiddleware
from devops.realtime.routing import websocket_urlpatterns
from channels.routing import URLRouter

application = ProtocolTypeRouter({
    'http': django_asgi_app,
    'websocket': JWTWebSocketMiddleware(
        URLRouter(websocket_urlpatterns)
    ),
})
