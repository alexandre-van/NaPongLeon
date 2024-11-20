from .utils.httpResponse import HttpResponseJD, HttpResponseRedirectJD, HttpResponseJDexception
from .services.OAuth42Service import async_oauth_42_service
import logging

logger = logging.getLogger(__name__)

async def OAuth42AuthorizeView(request):
    from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
    from django.conf import settings
    import secrets

    state = secrets.token_urlsafe(32)
    client_id = settings.OAUTH_42_CLIENT_ID
    redirect_uri = f"{settings.SITE_URL}/api/authentication/oauth/42/callback"
    '''
    state_token = str(RefreshToken.for_user(
        {"state": state}
    ).access_token)
    '''

    #auth_url = f"https://api.intra.42.fr/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code&state={state_token}"
    auth_url = f"https://api.intra.42.fr/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code"

    return HttpResponseRedirectJD(
        message='Redirect to 42 API',
        redirect_url=auth_url,
        status=200
    )



async def OAuth42CallbackView(request):
    try:
        code = request.GET.get('code')
        '''
        state_token = request.GET.get('state')
        logger.debug(f"OAuth42CallBack\ncode: {code}\n")
        if not code or not state_token:
            return HttpResponseJD('No code or state token provided', 400)

        try: # Validate state_token
            from rest_framework_simplejwt.tokens import AccessToken

            token = AccessToken(state_token)
            if 'state' not in token.payload:
                return HttpResponseJD('Invalid state token', 400)

        except Exception:
            return HttpResponseJD('Invalid state token', 400)
        '''
        
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
                max_age=60# * 60
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

