from .utils import HttpResponseJD, HttpResponseBadRequestJD
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

'''
from asgiref.sync import sync_to_async

class AsyncLoginConsumer(AsyncHttpConsumer):
    async def handle(self, body):
        if self.scope['method'] != 'POST':
            return HttpResponseBadRequestJD('Method not allowed')
        data = json.loads(await self.body_to_string(body))
        username = data.get('username')
        password = data.get('password')
        user = await sync_to_async(authenticate)(username=username, password=password)
        if user is not None:
            refresh = await sync_to_async(RefreshToken.for_user)(user)
            response = HttpResponseJD('Login successful', 200)
            response.set_cookie(
                'access_token',
                str(refresh.access_token),
                httponly=True,
                secure=False, # True for production
                samesite='Strict',
                max_age= 60 * 60
            )
            response.set_cookie(
                'refresh_token',
                str(refresh),
                httponly=True,
                secure=False,
                samesite='Strict',
                max_age= 24 * 60 * 60
            )

            csrf_token = await database_sync_to_async(get_token)(self.scope.get('session', {}))
            response['X-CSRFToken'] = csrf_token

            await self.update_user_status(user, True)
            return response
        else:
            return HttpResponseJD('Invalid credentials', 401)

    @database_sync_to_async
    def update_user_status(self, user, is_online):
        user.is_online = is_online
        user.save()
'''





async def Login_view(request):
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


async def UserNicknameView(request):
    logger.debug(f"request:{request}")
    if (request.method != 'PATCH'):
        return HttpRequestJD('Method not allowed', 405)

    try:
        data = json.loads(request.body)
        nickname = data.get('nickname')
    except json.JSONDecodeError:
        return HttpResponseBadRequestJD('Invalid JSON')

    user = request.user
    logger.debug(f"user:{user}")
    if user.is_authenticated:
        await user.update_nickname(nickname)
        return HttpResponseJD('Nickname updated', 204)
    return HttpResponseBadRequestJD('Anonymous user')

'''
#async def UserNicknameView(request):
class UserNicknameConsumer(AsyncHttpConsumer):
#class UserNicknameConsumer(AsyncConsumer):
    async def handle(self, body):
        logger.debug(f"request.method={self.scope['method']}")
        logger.debug(f"request={self.scope}")
        if self.scope['method'] != 'PATCH':
            return HttpResponseJD('Method not allowed', 405)

        try:
            data = json.loads(body.decode('utf-8'))
            nickname = data.get('nickname')
            logger.debug(f"data={data}")
        except json.JSONDecodeError:
            return HttpResponseBadRequestJD('Invalid JSON')

        user = self.scope.get('user', AnonymousUser())
        if not isinstance(user, AnonymousUser):
            await user.update_nickname(nickname)
            return HttpResponseJD('Nickname updated', 204)
        return HttpResponseBadRequestJD('Anonymous user')
'''