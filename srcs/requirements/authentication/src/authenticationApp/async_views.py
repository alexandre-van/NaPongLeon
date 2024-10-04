from .utils.httpResponse import HttpResponseJD, HttpResponseBadRequestJD
#from channels.generic.http import AsyncHttpConsumer
from channels.db import database_sync_to_async
from django.middleware.csrf import get_token
from django.contrib.auth import authenticate
from django.contrib.auth.models import AnonymousUser
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import JsonResponse
from asgiref.sync import sync_to_async
import json
import logging

logger = logging.getLogger(__name__)

async def LoginView(request):
    if request.method != 'POST':
        return HttpResponseBadRequestJD('Method not allowed')

    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
    except json.JSONDecodeError:
        return HttpResponseJD('Invalid JSON', 400)

    user = await database_sync_to_async(authenticate)(username=username, password=password)

    if user is not None:
        refresh = await database_sync_to_async(RefreshToken.for_user)(user)

        response = HttpResponseJD('Login successful', 200)
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

        # Log pour le débogage
        print(f"CSRF token stored in session during login: {csrf_token}")

        await user.update_user_status(True)
        return response
    else:
        return HttpResponseJD('Invalid credentials', 401)

async def LogoutView(request):
    if request.method != 'POST':
        return HttpResponseJD('Method not allowed', 405)
    user = request.user
    if user.is_authenticated:
        await user.update_user_status(False)
        response = HttpResponseJD('Logout successuful', 200)
        response.delete_cookie(
            'access_token',
        )
        response.delete_cookie(
            'refresh_token',
        )
        response.delete_cookie(
            'csrftoken',
        )
        return response
    return HttpResponseBadRequestJD('Anonymous user')

async def UserNicknameView(request):
    logger.debug(f"request:{request}")
    logger.debug(f"request.user:{request.user}")
    if request.method != 'PATCH':
        return HttpResponseJD('Method not allowed', 405)

    try:
        data = json.loads(request.body)
        nickname = data.get('nickname')
    except json.JSONDecodeError:
        return HttpResponseBadRequestJD('Invalid JSON')

    user = request.user
    logger.debug(f"user:{user}")
    logger.debug(f"user.is_authenticated ={user.is_authenticated}")
    if user.is_authenticated:
        await user.update_nickname(nickname)
        data = {
            'nickname': nickname
        }
        return HttpResponseJD('Nickname updated', 200, data)
    return HttpResponseBadRequestJD('Anonymous user')

