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
            (f"ASGIUserMiddleware: path={scope['path']}\n user={scope['user']}")
        else:
            (f"ASGIUserMiddleware: path={scope['path']}\n user not in scope")

        async def wrapped_receive():
            message = await receive()
            (f"message[type]={message['type']} with scope[user]={scope['user']}")
            if message['type'] == 'http.request':
                message['_user'] = scope.get('user', AnonymousUser())
            return message
            
        async def user_send(response):
            (f"response[type]={response['type']}")
            if response['type'] == 'http.response.start':
                if 'user' in scope:
                    response.setdefault('headers', []).append(
                        (b'X-User', str(scope['user']).encode())
                    )
                (f"ASGIUserMiddleware.user_send: scope[user]={scope['user']}")
            await send(response)

        ("Before result")
#        result = await self.inner(dict(scope, user=scope.get('user', AnonymousUser())), receive, user_send)
        result = await self.inner(scope, wrapped_receive, user_send)
        logger.debug("After result")
        return result
    '''

    async def __call__(self, scope, receive, send):
        if 'user' in scope:
            # Add user to scope['headers'] so it survives ASGI to WSGI transition
            scope.setdefault('headers', []).append(
                (b'asgi-user', str(scope['user']).encode())
            )
        else:
            logger.debug(f"ASGIUserMiddleware: path={scope['path']}, user not in scope")

        return await self.inner(scope, receive, send)

'''
@sync_and_async_middleware
class AsyncJWTAuthMiddleware:
    def __init__(self, inner):
        from authenticationApp.auth_middleware import CustomJWTAuthentication
        self.inner = inner
        self.auth = CustomJWTAuthentication()

    async def __call__(self, scope, receive, send):
        headers = dict(scope['headers'])
        logger.debug(f"\nAsyncJWTAuthMiddleware DEBUT\n")
        if b'cookie' not in headers:
            scope['user'] = AnonymousUser()
            return await self.inner(scope, receive, send)

        try:
            cookies = parse_cookies(headers.get(b'cookie', b'').decode())
            request = type('MockRequest', (), {
                'COOKIES': cookies,
                'META': normalize_headers(scope['headers']),
                'method': scope.get('method', ''),
                'path': scope.get('path', '')
            })

            access_token = request.COOKIES.get('access_token')
            refresh_token = request.COOKIES.get('refresh_token')
            logger.debug(f"access_token: {access_token}\n")
            logger.debug(f"refresh_token: {refresh_token}\n")

            async def get_new_access_token():
                from rest_framework_simplejwt.tokens import RefreshToken

                refresh = RefreshToken(refresh_token)
                new_access_token = str(refresh.access_token)
                logger.debug(f'new_access_token: {new_access_token}\n')

                scope['access_token'] = new_access_token

                request.COOKIES['access_token'] = new_access_token
                logger.debug(f'BEFORE AUTHENTICATE\n')
                user, validated_token = await sync_to_async(self.auth.authenticate)(request)
                logger.debug(f'AFTER AUTHENTICATE: user = {user}, validated_token = {validated_token}\n')
                scope['user'] = user
                logger.debug(f'scope[user]: {scope[user]}')
            
            if access_token:
                try:
                    user, validated_token = await sync_to_async(self.auth.authenticate)(request)
                    if validated_token:
                        scope['user'] = user

                    # If existing previous cookie
                except Exception as e:
                    logger.warning(f"Access token validation failed: {str(e)}")
                    if refresh_token:
                        try:
                            await get_new_access_token()

                        except Exception as refresh_error:
                            logger.warning(f"Refresh token validation failed: {str(e)}")
                            scope['user'] = AnonymousUser()
                            scope['clear_tokens'] = True
                    else:
                        scope['user'] = AnonymousUser()
            elif refresh_token:
                try:
                    logger.debug('REFRESH_TOKEN ///////////////////////\n')
                    await get_new_access_token()
                    logger.debug('APRES REFRESH_TOKEN ///////////////////////\n')
                
                except Exception as refresh_error:
                    logger.warning(f"Refresh token validation failed: {str(e)}")
                    scope['user'] = AnonymousUser()
                    scope['clear_tokens'] = True
            else:
                scope['user'] = AnonymousUser()

        except Exception as f:
            logger.warning(f"Error processing request: {str(f)}")
            scope['user'] = AnonymousUser()
        
        async def send_modifier(message):
            if message['type'] == 'http.response.start':
                headers = list(message.get('headers', []))
                logger.debug(f'\n\nheaders = {headers}\n\n')
                logger.debug(f'scope = {scope}\n\n')
                if 'access_token' in scope:
                    headers.append((
                        b'set-cookie',
                        f"access_token={scope['access_token']}; HttpOnly; SameSite=Strict; Max-Age=3600".encode()
                    ))
                elif scope.get('clear_tokens'):
                    headers.extend([
                        (b'set-cookie', b'access_token=; Max-Age=0')
                        (b'set-cookie', b'refresh_token=; Max-Age=0')
                    ])
                message['headers'] = headers
            await send(message)


        response = await self.inner(scope, receive, send_modifier)
        return response



'''
@sync_and_async_middleware
class AsyncJWTAuthMiddleware:
    def __init__(self, inner):
        from authenticationApp.auth_middleware import CustomJWTAuthentication
        self.inner = inner
        self.auth = CustomJWTAuthentication()

    async def __call__(self, scope, receive, send):
        headers = dict(scope['headers'])
        if b'cookie' not in headers:
            scope['user'] = AnonymousUser()
            return await self.inner(scope, receive, send)

        try:
            cookies = parse_cookies(headers.get(b'cookie', b'').decode())
            request = type('MockRequest', (), {
                'COOKIES': cookies,
                'META': normalize_headers(scope['headers']),
                'method': scope.get('method', ''),
                'path': scope.get('path', '')
            })

            access_token = request.COOKIES.get('access_token')
            refresh_token = request.COOKIES.get('refresh_token')

            # D'abord essayer l'access_token existant
            if access_token or refresh_token:
                try:
                    user, validated_token = await sync_to_async(self.auth.authenticate)(request)
                    scope['user'] = user
                    return await self.inner(scope, receive, send)
                except Exception as e:
                    logger.warning(f"Access token validation failed: {str(e)}")
                    # Si l'access_token est invalide/expiré, on essaie le refresh
                    if refresh_token:
                        try:
                            from rest_framework_simplejwt.tokens import RefreshToken
                            refresh = RefreshToken(refresh_token)
                            scope['access_token'] = str(refresh.access_token)
                            request.COOKIES['access_token'] = scope['access_token']
                            user, validated_token = await sync_to_async(self.auth.authenticate)(request)
                            scope['user'] = user
                        except Exception as refresh_error:
                            logger.warning(f"Refresh token validation failed: {str(refresh_error)}")
                            scope['user'] = AnonymousUser()
                            scope['clear_tokens'] = True
                    else:
                        scope['user'] = AnonymousUser()
            else:
                scope['user'] = AnonymousUser()

        except Exception as e:
            logger.warning(f"Error processing request: {str(e)}")
            scope['user'] = AnonymousUser()

        return await self.inner(scope, receive, self.get_send_wrapper(send, scope))

    def get_send_wrapper(self, send, scope):
        async def send_wrapper(message):
            if message['type'] == 'http.response.start':
                headers = list(message.get('headers', []))
                if 'access_token' in scope:
                    headers.append((
                        b'set-cookie',
                        f"access_token={scope['access_token']}; HttpOnly; SameSite=Strict; Max-Age=7200; Path=/".encode()
                    ))
                elif scope.get('clear_tokens'):
                    headers.extend([
                        (b'set-cookie', b'access_token=; Max-Age=0; Path=/'),
                        (b'set-cookie', b'refresh_token=; Max-Age=0; Path=/')
                    ])
                message['headers'] = headers
            await send(message)
        return send_wrapper



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
        exempt_paths = [
            '/api/authentication/auth/login/',
            '/api/authentication/users/',
            '/api/authentication/oauth/42/callback/',
            '/api/authentication/oauth/42/authorize/',
            '/api/authentication/verify_token/',
        ]
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
        if getattr(request, 'csrf_exempt', False):
            setattr(request, '_dont_enforce_csrf_checks', True)
        return self.get_response(request)
