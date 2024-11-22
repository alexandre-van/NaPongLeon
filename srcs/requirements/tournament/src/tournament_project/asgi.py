"""
ASGI config for tournament project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
django_http_server = get_asgi_application()

from tournament_app.routing import websocket_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tournament_project.settings')

application = ProtocolTypeRouter({
			"http": django_http_server,
			"websocket": AuthMiddlewareStack(
				URLRouter(
					websocket_urlpatterns
				)
			),
})
