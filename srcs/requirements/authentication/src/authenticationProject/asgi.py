"""
ASGI config for authenticationProject project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'authenticationProject.settings')
django_http_server = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter
from authenticationApp.routing import websocket_urlpatterns
from authenticationApp.middlewares.asgi_middleware import ASGIUserMiddleware, AsyncJWTAuthMiddleware, AsyncJWTAuthMiddlewareStack, CsrfAsgiMiddleware 

application = ProtocolTypeRouter({
    "http": CsrfAsgiMiddleware(
        AsyncJWTAuthMiddleware(
            ASGIUserMiddleware(django_http_server)
        )
    ),
    "websocket": AsyncJWTAuthMiddlewareStack(URLRouter(websocket_urlpatterns)),
})
