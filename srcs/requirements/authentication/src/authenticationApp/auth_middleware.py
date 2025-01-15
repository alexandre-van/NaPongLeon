from rest_framework_simplejwt.authentication import JWTAuthentication
from asgiref.sync import sync_to_async
from django.conf import settings
from asgiref.sync import sync_to_async

import logging

logger = logging.getLogger(__name__)


class CustomJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        header = self.get_header(request)

        if header is None:
            raw_token = request.COOKIES.get(settings.SIMPLE_JWT['AUTH_COOKIE']) or None
        else:
            raw_token = self.get_raw_token(header)

        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)
        return self.get_user(validated_token), validated_token
        


class AsyncCustomJWTAuthentication(JWTAuthentication):
    async def authenticate(self, request):
        logger.debug('1')
        header = self.get_header(request)

        logger.debug('2')
        if header is None:
            logger.debug('3')
            raw_token = request.COOKIES.get(settings.SIMPLE_JWT['AUTH_COOKIE']) or None
        else:
            logger.debug('4')
            raw_token = self.get_raw_token(header)

        if raw_token is None:
            logger.debug('5')
            return None
        
        logger.debug('bonjour')
        validated_token = await sync_to_async(self.get_validated_token)(raw_token)
        logger.debug('avant return')
        return await sync_to_async(self.get_user)(validated_token), validated_token
