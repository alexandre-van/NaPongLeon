from channels.db import database_sync_to_async

import logging

logger = logging.getLogger(__name__)

async def create_login_response(user, request):
    from .httpResponse import HttpResponseJD
    from rest_framework_simplejwt.tokens import RefreshToken
    from django.middleware.csrf import get_token
    from datetime import timedelta
    from django.utils import timezone

    refresh = await database_sync_to_async(RefreshToken.for_user)(user)
    refresh.access_token.set_exp(from_time=timezone.now(), lifetime=timedelta(minutes=1))

    response = HttpResponseJD('Login successful', 200)
    response.set_cookie(
        'access_token',
        str(refresh.access_token),
        httponly=True,
        secure=False,  # True for production
        samesite='Strict',
        max_age=60
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
    (f"\n\n\n\n\nCREATE_LOGIN_RESPONSE\nresponse={response}")
    return response



async def setup_2fa(user):
    # Setup TOTP device for user
    from django_otp.plugins.otp_totp.models import TOTPDevice

    device = await database_sync_to_async(TOTPDevice.objects.create)(
        user=user,
        name=f"Default device for {user.username}",
        confirmed=False
    )
    config_url = device.config_url
    return config_url



async def validate_totp(user, token):
    from django_otp import devices_for_user
    from asgiref.sync import sync_to_async

    @sync_to_async
    def check_token(user, token):
        for device in devices_for_user(user, confirmed=True):
            if device.verify_token(token):
                return True
        return False
    
    return await check_token(user, token)