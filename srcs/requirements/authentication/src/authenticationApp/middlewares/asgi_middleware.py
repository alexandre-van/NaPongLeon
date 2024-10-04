from channels.auth import AuthMiddlewareStack
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware

from django.middleware.csrf import get_token, rotate_token
from django.contrib.auth.models import AnonymousUser
from authenticationApp.models import CustomUser
from django.conf import settings
from django.http import HttpRequest, JsonResponse
from django.utils.decorators import sync_and_async_middleware

from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

from asgiref.sync import sync_to_async

from .utils import parse_cookies, normalize_headers
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
    def __init__(self, inner):
        self.inner = inner

    '''
    async def __call__(self, scope, receive, send):
        if 'user' in scope:
            logger.debug(f"ASGIUserMiddleware: path={scope['path']}\n user={scope['user']}")
        else:
            logger.debug(f"ASGIUserMiddleware: path={scope['path']}\n user not in scope")

        async def wrapped_receive():
            message = await receive()
            logger.debug(f"message[type]={message['type']} with scope[user]={scope['user']}")
            if message['type'] == 'http.request':
                message['_user'] = scope.get('user', AnonymousUser())
            return message
            
        async def user_send(response):
            logger.debug(f"response[type]={response['type']}")
            if response['type'] == 'http.response.start':
                if 'user' in scope:
                    response.setdefault('headers', []).append(
                        (b'X-User', str(scope['user']).encode())
                    )
                logger.debug(f"ASGIUserMiddleware.user_send: scope[user]={scope['user']}")
            await send(response)

        logger.debug("Before result")
#        result = await self.inner(dict(scope, user=scope.get('user', AnonymousUser())), receive, user_send)
        result = await self.inner(scope, wrapped_receive, user_send)
        logger.debug("After result")
        return result
    '''

    async def __call__(self, scope, receive, send):
        if 'user' in scope:
            logger.debug(f"ASGIUserMiddleware: path={scope['path']}, user={scope['user']}")
            # Add user to scope['headers'] so it survives ASGI to WSGI transition
            scope.setdefault('headers', []).append(
                (b'asgi-user', str(scope['user']).encode())
            )
        else:
            logger.debug(f"ASGIUserMiddleware: path={scope['path']}, user not in scope")

        return await self.inner(scope, receive, send)

@sync_and_async_middleware
class AsyncJWTAuthMiddleware:
    def __init__(self, inner):
        from authenticationApp.auth_middleware import CustomJWTAuthentication
        self.inner = inner
        self.auth = CustomJWTAuthentication()

    async def __call__(self, scope, receive, send):
        headers = dict(scope['headers'])
        logger.debug(f"headers:{headers}")
        if b'cookie' in headers:
            try:
                cookies = parse_cookies(headers.get(b'cookie', b'').decode())
                #token_name, token_key = headers[b'cookie'].decode().split()
                request = type('MockRequest', (), {
                    'COOKIES': cookies,
                    'META': normalize_headers(scope['headers']),
                    'method': scope.get('method', ''),
                    'path': scope.get('path', '')
                })
                logger.debug(f"COOKIES:{request.COOKIES}")
                access_token = request.COOKIES.get('access_token')
                logger.debug(f"access_token:{access_token}")

                user, validated_token = await sync_to_async(self.auth.authenticate)(request)
                if validated_token:
                    scope['user'] = user
                

#                if token_name == 'access_token':
#                    validated_token = UntypedToken(token_key)
                #scope['user'] = await get_user(validated_token)
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
        cookies = parse_cookies(headers.get(b'cookie', b'').decode())
        
        normalized_headers = normalize_headers(scope['headers'])
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

        async def server_send(response):
            logger.debug(f"response={response}")
            await send(response)
        
        return await self.get_response(scope, receive, server_send)

    def get_csrf_header(self, headers):
        return (headers.get('HTTP_X_CSRFTOKEN') or 
                headers.get('HTTP_X_CSRF_TOKEN') or 
                headers.get('X_CSRFTOKEN') or 
                headers.get('X_CSRF_TOKEN'))

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