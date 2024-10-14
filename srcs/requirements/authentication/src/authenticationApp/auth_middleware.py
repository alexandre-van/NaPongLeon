from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.utils.functional import SimpleLazyObject
from django.contrib.auth.models import AnonymousUser
from asgiref.sync import sync_to_async
from django.conf import settings

import logging

logger = logging.getLogger(__name__)

class CustomJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        header = self.get_header(request)
        logger.debug(f"request: {request}")
        logger.debug(f"request.COOKIES: {request.COOKIES}")

        if header is None:
            raw_token = request.COOKIES.get(settings.SIMPLE_JWT['AUTH_COOKIE']) or None
            logger.debug(f"raw_token: {raw_token}")
        else:
            raw_token = self.get_raw_token(header)

        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)
        return self.get_user(validated_token), validated_token
        

class JWTAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.jwt_auth = CustomJWTAuthentication()

    async def __call__(self, request):
        # When request.user called in a view, it will be sent here
        request.user = SimpleLazyObject(lambda: self._get_user(request))
        response = await self.get_response(request)
        return response

    @sync_to_async
    def _get_user(self, request):
        # check if user is already in request's cache
        user = getattr(request, '_cached_user', None)
        if user is not None:
            return user
        # if not then checks with db
        auth_result = self.jwt_auth.authenticate(request)
        if auth_result is not None:
            user, _ = auth_result
        else:
            user = AnonymousUser()

        request._cached_user = user
        return user


class AutoRefreshTokenMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        access_token = request.COOKIES.get('access_token')
        refresh_token = request.COOKIES.get('refresh_token')

        if access_token and refresh_token:
            try:
                # Try to validate the access token
                AccessToken(access_token).verify()
            except:
                # Try to refresh invalid access_token
                try:
                    refresh = RefreshToken(refresh_token)
                    access_token = str(refresh.access_token)

                    request.COOKIES['access_token'] = access_token
                    response = self.get_response(request)
                    response.set_cookie(
                        'access_token',
                        access_token,
                        httponly=True,
                        secure=False,
                        samesite='Strict',
                        max_age=60 * 60
                    )
                    return response
                except (InvalidToken, TokenError):
                    # if invalid refresh_token, remove all
                    response = self.get_response(request)
                    response.delete_cookie('access_token')
                    response.delete_cookie('refresh_token')
                    return response

        logger.debug("AutoRefreshTokenMiddleware fin")
        # If valid access_token or no token at all
        return self.get_response(request)

from asgiref.sync import sync_to_async

class AsyncCustomJWTAuthentication(JWTAuthentication):
    async def authenticate(self, request):
        header = self.get_header(request)

        if header is None:
            raw_token = request.COOKIES.get(settings.SIMPLE_JWT['AUTH_COOKIE']) or None
        else:
            raw_token = self.get_raw_token(header)

        if raw_token is None:
            return None
        
        validated_token = await sync_to_async(self.get_validated_token)(raw_token)
        return await sync_to_async(self.get_user)(validated_token), validated_token
