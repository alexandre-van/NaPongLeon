from channels.auth import AuthMiddlewareStack
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware

from django.middleware.csrf import get_token, rotate_token
from django.contrib.auth.models import AnonymousUser
from django.conf import settings
from django.http import HttpRequest

from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

from jwt import decode as jwt_decode
import hmac

import logging

logger = logging.getLogger(__name__)

@database_sync_to_async
def get_user(validated_token):
    try:
        user = CustomUser.objects.get(id=validated_token["user_id"])
        return user
    except CustomUser.DoesNotExist:
        return AnonymousUser()

def compare_salted_tokens(token1, token2):
    return hmac.compare_digest(token1, token2)

class AsyncJWTAuthMiddleware:
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        headers = dict(scope['headers'])
        if b'authorization' in headers:
            try:
                token_name, token_key = headers[b'authorization'].decode().split()
                if token_name == 'Bearer':
                    validated_token = UntypedToken(token_key)
                    scope['user'] = await get_user(validated_token)
            except (InvalidToken, TokenError) as e:
                scope['user'] = AnonymousUser()
        else:
            scope['user'] = AnonymousUser()

        return await self.inner(scope, receive, send)

def AsyncJWTAuthMiddlewareStack(inner):
    return AsyncJWTAuthMiddleware(AuthMiddlewareStack(inner))



# CSRF token
class CsrfAsgiMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        if scope['type'] == 'http':
            headers = dict(scope['headers'])
            '''
            csrf_token = None
            for name, value in headers.items():
                if name.decode().lower() == 'x-csrftoken':
                    csrf_token = value.decode()
                    break
            '''
            path = scope.get('path', '')
            method = scope.get('method', '')

            logger.debug(f"path: {path}, method: {method}")

            # Create simulated HTTP request
            request = HttpRequest()
            request.META = {key.decode().upper().replace('-', '_'): value.decode() for key, value in headers.items()}
            request.method = method
            request.path = path

            # Manage CSRF cookie
            if 'csrftoken' not in request.COOKIES:
                csrf_token = get_token(request)
                scope['headers'] += [(b'Set-Cookie', f'csrftoken={csrf_token}; Path=/; HttpOnly; SameSite=Strict'.encode())]
            

            # Exempt login route from this check
            exempt_paths = ['/api/authentication/auth/login/', '/api/authentication/users/']
            if path in exempt_paths and method == 'POST':
                # Add a marker to show this request as exempt
                scope['csrf_exempt'] = True
                logger.debug(f"CSRF exemption applied for {path}")

                async def wrapped_send(event):
                    if event['type'] == 'http.response.start':
                        headers = event.get('headers', [])
                        headers.append((b'X-CSRFExempt', b'1'))
                        event['headers'] = headers
                    await send(event)

                return await super().__call__(scope, receive, wrapped_send)

            # Check CSRF for all other routes
            if method in ['POST', 'PUT', 'DELETE', 'PATCH']:
                csrf_token = request.META.get('HTTP_X_CSRFTOKEN')
                if not csrf_token or csrf_token != get_token(request):
                    logger.debug(f"CSRF verification failed for {path}")
                    return await self.send_csrf_failure(send)

            session = scope.get('session', {})
            logger.debug(f"session: {session}")
            if scope['method'] in ['POST', 'PUT', 'DELETE', 'PATCH']:
                if not csrf_token or not compare_salted_tokens(csrf_token, get_token(session)):
                    return await self.send_csrf_failure(send)
            logger.debug("reussi")
        return await super().__call__(scope, receive, send)

    async def send_csrf_failure(self, send):
        await send({
            'type': 'http.response.start',
            'status': 403,
            'headers': [(b'content-type', b'text/plain')],
        })
        await send({
            'type': 'http.response.body',
            'body': b'CSRF verification failed',
        })

# Middleware to deactivate CSRF check of Django
class CsrfExemptMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if getattr(request, 'csrf_exempt', False):
            setattr(request, '_dont_enforce_csrf_checks', True)
        return self.get_response(request)

