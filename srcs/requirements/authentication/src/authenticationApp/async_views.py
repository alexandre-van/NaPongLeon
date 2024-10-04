from .utils.httpResponse import HttpResponseJD, HttpResponseBadRequestJD, HttpResponseJDexception
#from channels.generic.http import AsyncHttpConsumer
from channels.db import database_sync_to_async
from django.middleware.csrf import get_token
from django.contrib.auth import authenticate
from django.contrib.auth.models import AnonymousUser
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import JsonResponse
from asgiref.sync import sync_to_async

# Image loading
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from PIL import Image
import io

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

async def UserAvatarView(request):
    if request.method == 'GET':
        user = request.user
        if user.avatar:
            logger.debug(f"Avatar_url: {user.avatar.url}")
            return HttpResponseJD('Avatar found', 200, user.avatar.url)
        else:
            logger.debug("No avatar found")
            return HttpResponseJD('No avatar found', 404)
    elif request.method == 'POST':
        if 'avatar' not in request.FILES:
            return HttpResponseBadRequestJD('No file uploaded')

        file = request.FILES['avatar']
        allowed_types = ['image/jpeg', 'image/png']
        if file.content_type not in allowed_types:
            return HttpResponseBadRequestJD('Invalid file type. Only JPEG and PNG are allowed.')

        if file.size > 1024 * 1024:
            return HttpResponseBadRequestJD('File too large. Maximum size is 1MB')
        
        try:
            img = Image.open(file)

            # Resize 500x500
            img.thumbnail((500, 500))

            # For transparent imgs
            if img.mode != 'RGB':
                img = img.convert('RGB')

            buffer = io.BytesIO()
            img.save(buffer, format='JPEG')
            buffer.seek(0)

            user = request.user
            filename = f"avatar_{user.id}.jpg"
            filepath = f"users/{user.id}/avatar/{filename}"

            logger.debug(f"filepath: {filepath}")
            # Check if file already exists, if true, deletes it and saves the new one
            if user.avatar:
                await sync_to_async(default_storage.delete)(user.avatar.name)

            new_path = await sync_to_async(default_storage.save)(filepath, ContentFile(buffer.read()))
            await user.update_avatar_url(new_path)

            return HttpResponseJD('Avatar uploaded successfully', 200)
            
        except IOError:
            return HttpResponseBadRequestJD('Unable to process the image')

        except Exception as e:
            return HttpResponseJDexception(e)
    else:
        return HttpResponseJD('Method not allowed', 405)
            