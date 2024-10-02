#from django.shortcuts import render
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect
from django.utils.decorators import method_decorator
from django.middleware.csrf import get_token
from django.http import HttpRequest
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from .utils import HttpResponseJD, HttpResponseBadRequestJD, HttpResponseNotFoundJD, HttpResponseJDexception
from .models import CustomUser
from .serializers import UserSerializer, FriendshipSerializer
from authenticationApp.auth_middleware import CustomJWTAuthentication
from authenticationApp.services.AsyncJWTChecks import AsyncCustomJWTAuthentication, AsyncIsAuthenticated
#from .async_views import AsyncLoginConsumer

from .services.FriendRequestService import FriendRequestService

from channels.layers import get_channel_layer
from asgiref.sync import sync_to_async, async_to_sync


from channels.db import database_sync_to_async
from django.contrib.auth import authenticate
from django.http import JsonResponse


from PIL import Image
import io
import os
import json
import logging

logger = logging.getLogger(__name__)

class UserView(APIView):
    # These two methods are used to check the JWT when method is 'GET'
    def get_permissions(self):
        if self.request.method == 'POST':
            return []
        return [permissions.IsAuthenticated()]

    def get_authenticators(self):
        if self.request.method == 'POST':
            return []
        return [CustomJWTAuthentication()]

    # Registration without checking JWT
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({'message': 'Registration success'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Get User info
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response({
            "user": serializer.data
        }, status=status.HTTP_200_OK)

'''
@async_to_sync
async def Login_view(request):
    scope = {
        'type': 'http',
        'method': request.method,
        'path': request.path,
        'headers': [[key.encode(), value.encode()] for key, value in request.headers.items()],
        'query_string': request.META.get('QUERY_STRING', '').encode(),
    }
    consumer = AsyncLoginConsumer(scope)
    response = await consumer.handle(request.body)
    return response
'''

'''
def Login_view(request):
    async def _login_view(request):
        asgi_request = AsgiHandler()(request)
        consumer = AsyncLoginConsumer()
        response = await consumer.handle(asgi_request['body'])
        return response

    return async_to_sync(_login_view)(request)
'''

'''
@method_decorator(ensure_csrf_cookie, name='dispatch')
class LoginView(APIView):
    async def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = await sync_to_async(authenticate)(username=username, password=password)

        if user is not None:
            refresh = await sync_to_async(RefreshToken.for_user)(user)
            response = Response({'message': 'Login successful'})

            # Short-term Access token
            response.set_cookie(
                'access_token',
                str(refresh.access_token),
                httponly=True,
                secure=False, # True for production
                samesite='Strict',
                max_age=60 * 60 # 60 mins * 60 sec
            )

            # Long-term Refresh token
            response.set_cookie(
                'refresh_token',
                str(refresh),
                httponly=True,
                secure=False,
                samesite='Strict',
                max_age=24 * 60 * 60 # 1 day
            )
            return response
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
'''


class WebSocketTokenView(APIView):
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Short access_token for user
        token = AccessToken.for_user(request.user)
        return Response({'token': str(token)})



class TokenRefreshView(APIView):
    def post(self, request):
        refresh_token = request.COOKIES>get('refresh_token')
        if refresh_token is None:
            return Response({'error': 'Refresh token not found'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)
            
            response = Response({'message': 'Token refreshed successfully'})
            response.set_cookie(
                'access_token',
                access_token,
                httponly=True,
                secure=False,
                samesite='Strict',
                max_age=60 * 60
            )
            return response
        except TokenError:
            return Response({'error': 'Invalid refresh token'}, status=status.HTTP_401_UNAUTHORIZED)



class LogoutView(APIView):
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.user.is_online = False
        response = Response({"detail": "Logout successful"}, status=status.HTTP_200_OK)
        response.delete_cookie(
            'access_token',
            #httponly=True,
            #secure=False,
            #samesite='Strict'
        )
        response.delete_cookie(
            'refresh_token',
            #httponly=True,
            #secure=False,
            #samesite='Strict'
        )
        response.delete_cookie(
            'csrftoken',
        )
        
        return response



class UserAvatarView(APIView):
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated]

    # Get avatar_url
    def get(self, request):
        user = request.user
        if user.avatar:
            logger.debug(f"Avatar_url: {user.avatar.url}")
            return Response({'avatar_url': user.avatar_url}, status=status.HTTP_200_OK)
        else:
            logger.debug("No avatar found")
            return Response({'error': 'No avatar found'}, status=status.HTTP_404_NOT_FOUND)

    # Update avatar_url
    def post(self, request):
        if 'avatar' not in request.FILES:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        file = request.FILES['avatar']

        allowed_types = ['image/jpeg', 'image/png']
        if file.content_type not in allowed_types:
            return Response({'error': 'Invalid file type. Only JPEG and PNG are allowed'}, status=status.HTTP_400_BAD_REQUEST)

        if file.size > 5 * 1024 * 1024:
#            logger.warning(f"File too large: {file.size}")
            return Response({'error': 'File too large. Maximum size is 5MB'}, status=status.HTTP_400_BAD_REQUEST)

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
            filepath = f"users/{user.id} /avatar/{filename}"

            # Check if file already exists, if true, deletes it and saves the new one
            if user.avatar:
                default_storage.delete(user.avatar.name)

            new_path = default_storage.save(filepath, ContentFile(buffer.read()))

            user.avatar = new_path
            user.save()

            avatar_url = request.build_absolute_uri(user.avatar.url)
            return Response({
                'message': 'Avatar uploaded successfully'}, status=status.HTTP_200_OK)

        except IOError:
            return Response({'error': 'Unable to process the image'}, status=status.HTTP_400_BAD_REQUEST) 

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



'''
class UserNicknameView(APIView):
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        nickname = request.data.get('nickname')
        serializer = UserSerializer(request.user, data={'nickname': request.data.get('nickname')}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'nickname': serializer.validated_data['nickname']
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
'''



# Friends related views

class FriendsView(APIView):
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated]

    # Get All Friends
    def get(self, request):
        pass



async def FriendsRequestView(request):
    # Get waiting requests
    logger.debug(f"request.method: {request.method}")

    if request.method == "GET":
        return HttpResponseJD('Get method not implemented yet', 501)

    elif request.method == "POST":
    # Send a friend request
        sender = await sync_to_async(lambda: request.user)()
        body = request.body

        logger.debug(f"sender: {sender}")
        logger.debug(f"request.body: {request.body}")
        try:
            data = json.loads(body)
            logger.debug(f"data: {data}")
        except json.JSONDecodeError:
            return HttpResponseBadRequestJD('Invalid JSON')

        receiver_username = data.get('target_user')
        logger.debug(f"request_username: {receiver_username}")
        if not receiver_username:
            return HttpResponseBadRequestJD('Username needed')
        try:
            receiver = await sync_to_async(CustomUser.objects.get)(username=receiver_username)
        except CustomUser.DoesNotExist:
            return HttpResponseNotFoundJD('Target user does not exist')
        if sender == receiver:
            return HttpResponseBadRequestJD('Cannot be yourself')
        logger.debug(f"sender: {sender}")
        logger.debug(f"receiver: {receiver}")

        try:
            result = await FriendRequestService.create_and_send_friend_request(sender, receiver)
            if result:
                return HttpResponseJD('Friend request sent', 201)
            else:
                return HttpResponseJD('Friend request already exists', 409)
        except Exception as e:
            return HttpResponseJDexception(e)
    elif request.method == "PATCH":
    # Accept a friend request
        return HttpResponseJD('Patch method not implemented yet', 501)
    elif request.method == "DELETE":
    # Refuse or cancel a friend request
        return HttpResponseJD('Delete method not implemented yet', 501)
    else: 
        return HttpResponseJD('Method not allowed', 405)


class UserFriendView(APIView):
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated]

    # Get Friend list
    def get(self, request):
        pass

    # Delete Friend
    def delete(self, request, friend_id):
        pass 

