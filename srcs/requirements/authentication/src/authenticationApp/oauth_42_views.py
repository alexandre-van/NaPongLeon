from .utils.httpResponse import HttpResponseJD, HttpResponseRedirectJD, HttpResponseJDexception
from .services.OAuth42Service import async_oauth_42_service
import logging

logger = logging.getLogger(__name__)

async def OAuth42CallbackView(request):
    try:
        code = request.GET.get('code')
        logger.debug(f"OAuth42CallBack\ncode: {code}\n")
        if not code:
            return HttpResponseJD('No code provided', 400)
        
        async with async_oauth_42_service as service:
            from channels.db import database_sync_to_async
            from django.middleware.csrf import get_token
            from rest_framework_simplejwt.tokens import RefreshToken

            logger.debug('0\n')
            access_token = await service.exchange_code_for_token(code)

            logger.debug(f'1 access_token: {access_token}\n')
            user_data = await service.get_user_data(access_token)

            logger.debug('2\n')
            user = await service.get_or_create_user(user_data)

            logger.debug('3\n')
            refresh = await database_sync_to_async(RefreshToken.for_user)(user)

            logger.debug('4\n')
            response = HttpResponseRedirectJD(
                message='Login successful',
                redirect_url='/login/success',
                status=200
            )
            response.set_cookie(
                'access_token',
                str(refresh.access_token),
                httponly=True,
                secure=False,  # True for production
                samesite='Strict',
                max_age=60 * 60
            )
            response.set_cookie(
                'refresh_token',
                str(refresh),
                httponly=True,
                secure=False,
                samesite='Strict',
                max_age=24 * 60 * 60
            )
            csrf_token = get_token(request)
            response.set_cookie(
                'csrftoken',
                csrf_token,
                httponly=False,
                secure=False,  # True for production
                samesite='Strict'
            )
            response['X-CSRFToken'] = csrf_token
            
            return response

    except Exception as e:
        logger.debug(f"Could not get or create user via 42: {str(e)}")
        return HttpResponseJDexception('Could not get or create user via 42')

