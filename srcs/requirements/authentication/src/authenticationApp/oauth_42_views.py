from .utils.httpResponse import HttpResponseJD, HttpResponseRedirectJD, HttpResponseJDexception
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from .services.OAuth42Service import async_oauth_42_service
from django.conf import settings
from datetime import datetime, timedelta
import secrets
import logging

logger = logging.getLogger(__name__)

async def OAuth42AuthorizeView(request):
    """
    Initialize OAuth process statelessly
    """
    raw_state = secrets.token_urlsafe(32)
    
    # Create a JWT which contains all necessary informations
    state_token = AccessToken()
    state_token['state'] = raw_state
    state_token['nonce'] = secrets.token_urlsafe(16)
    state_token['initiated_at'] = datetime.now().timestamp()
    state_token.set_exp(lifetime=timedelta(minutes=10))
    
    auth_url = (
        f"https://api.intra.42.fr/oauth/authorize"
        f"?client_id={settings.OAUTH_42_CLIENT_ID}"
        f"&redirect_uri={settings.SITE_URL}/api/authentication/oauth/42/callback"
        f"&response_type=code"
        f"&state={str(state_token)}"
    )
    
    return HttpResponseRedirectJD(
        message='Redirect to 42 API',
        redirect_url=auth_url,
        status=200
    )

async def OAuth42CallbackView(request):
    """
    Manage OAuth callback statelessly
    """
    try:
        code = request.GET.get('code')
        state_token = request.GET.get('state')
        
        if not code or not state_token:
            return HttpResponseJD('Missing code or state', 400)
        
        try:
            # Validate JWT state token
            token = AccessToken(state_token)
            
            # Verify expiration date
            if datetime.now().timestamp() > token['exp']:
                return HttpResponseJD('State token expired', 400)
            
            # Check the lifetime of the token < 10 mins
            time_elapsed = datetime.now().timestamp() - token['initiated_at']
            if time_elapsed > 600:  # 10 mins
                return HttpResponseJD('Authentication flow took too long', 400)
            
        except Exception as e:
            logger.error(f"State validation failed: {e}")
            return HttpResponseJD('Invalid state token', 400)
        
        async with async_oauth_42_service as service:
            from channels.db import database_sync_to_async
            from django.middleware.csrf import get_token
            from django.utils import timezone
            from datetime import timedelta
            import pytz

            access_token = await service.exchange_code_for_token(code)
            user_data = await service.get_user_data(access_token)
            user = await service.get_or_create_user(user_data)

            refresh = await database_sync_to_async(RefreshToken.for_user)(user)

            cet = pytz.timezone('CET')

            refresh.access_token.set_exp(from_time=timezone.now(), lifetime=timedelta(minutes=5))
            
            
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
                max_age=300
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
                secure=True,
                samesite='Strict'
            )
            response['X-CSRFToken'] = csrf_token

            return response
            
    except Exception as e:
        logger.error(f"OAuth process failed: {e}")
        return HttpResponseJDexception('Authentication failed')