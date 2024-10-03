from channels.auth import AuthMiddlewareStack
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware

from django.middleware.csrf import get_token, rotate_token
from django.contrib.auth.models import AnonymousUser
from django.conf import settings
from django.http import HttpRequest, JsonResponse
from django.utils.decorators import sync_and_async_middleware

from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

from django.core.handlers.asgi import ASGIHandler

from jwt import decode as jwt_decode
import hmac
import json

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

class ASGIUserMiddleware:
    '''
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        if 'user' in scope:
            scope['_user'] = scope['user']

        async def user_middleware(request):
            if hasattr(scope, '_user'):
                request.user = scope['_user']
            return await self.inner(request)

        return await user_middleware(scope['request'])
    '''
    def __init__(self, inner):
        self.inner = ASGIHandler()

    async def __call__(self, scope, receive, send):
        if 'user' in scope:
            scope['_user'] = scope['user']

        async def user_send(response):
            if response['type'] == 'http.response.start':
                if '_user' in scope:
                    response.setdefault('headers', []).append(
                        (b'X-User', str(scope['_user']).encode())
                    )
            await send(response)

        await self.inner(dict(scope, user=scope.get('_user', AnonymousUser())), receive, user_send)

class AsyncJWTAuthMiddleware:
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        headers = dict(scope['headers'])
        logger.debug(f"headers:{headers}")
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

        logger.debug(f"avant les views scope[user]: {scope['user']}")
        response = await self.inner(scope, receive, send)
        logger.debug('apres les views')
        return response

def AsyncJWTAuthMiddlewareStack(inner):
    return AsyncJWTAuthMiddleware(AuthMiddlewareStack(inner))

@sync_and_async_middleware
class CsrfAsgiMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    async def __call__(self, scope, receive, send):
        if scope['type'] != 'http':
            return await self.get_response(scope, receive, send)

        # Create a mock request object
        headers = dict(scope['headers'])
        cookies = self.parse_cookies(headers.get(b'cookie', b'').decode())
        
        normalized_headers = self.normalize_headers(scope['headers'])
        request = type('MockRequest', (), {
            'COOKIES': cookies,
            'META': normalized_headers,
            'method': scope.get('method', ''),
            'path': scope.get('path', '')
        })


        # Exempt routes
        exempt_paths = ['/api/authentication/auth/login/', '/api/authentication/users/']
        if request.path in exempt_paths:
            response = await self.get_response(scope, receive, send)
            return response

        # Check JWT (assuming you have a function to do this)
        #if not self.validate_jwt(request):
        #    return JsonResponse({'error': 'Invalid or missing JWT'}, status=401)

        # Check CSRF for state-changing methods
        if request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
            csrf_cookie = request.COOKIES.get('csrftoken')
            csrf_header = self.get_csrf_header(normalized_headers)
            if not csrf_cookie or not csrf_header or csrf_cookie != csrf_header:
                return await self.send_error_response(send, 'CSRF token missing or invalid', 403)
        
        return await self.get_response(scope, receive, send)
    
    def normalize_headers(self, headers):
        return {
            f"HTTP_{key.decode('ascii').upper().replace('-', '_')}": value.decode('ascii')
            for key, value in headers
        }

    def get_csrf_header(self, headers):
        return (headers.get('HTTP_X_CSRFTOKEN') or 
                headers.get('HTTP_X_CSRF_TOKEN') or 
                headers.get('X_CSRFTOKEN') or 
                headers.get('X_CSRF_TOKEN'))

    def parse_cookies(self, cookie_string):
        if not cookie_string:
            return {}
        return {
            k.strip(): v.strip() 
            for k, v in (pair.split('=', 1) for pair in cookie_string.split(';')) 
            if k and v
        }

    async def send_error_response(self, send, message, status):
        await send({
            'type': 'http.response.start',
            'status': status,
            'headers': [(b'content-type', b'application/json')],
        })
        await send({
            'type': 'http.response.body',
            'body': JsonResponse({'error': message}).content,
        })

# Middleware to deactivate CSRF check of Django
class CsrfExemptMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        logger.debug('CsrfExemptMiddleware')
        if getattr(request, 'csrf_exempt', False):
            setattr(request, '_dont_enforce_csrf_checks', True)
        return self.get_response(request)