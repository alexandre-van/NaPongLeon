#from django.shortcuts import render
from django.contrib.auth import authenticate
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import CustomUser
from .serializers import UserSerializer
from authenticationApp.auth_middleware import CustomJWTAuthentication

from PIL import Image
import io
import os

import logging

logger = logging.getLogger(__name__)

class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'user_id': user.id,
                'username': user.username,
                'message': 'User registered successfully'
            }, status=status.HTTP_201_CREATED)
        logger.info("Received registration request")
        logger.debug(f"Request data: {request.data}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)

        if user is not None:
            refresh = RefreshToken.for_user(user)
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

class LogoutView(APIView):
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
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
        return response

class CheckAuthView(APIView):
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated] # if not, returns HTTP_401_UNAUTHORIZED

    def get(self, request):
        return Response({
            "user": {
                "id": request.user.id,
                "username": request.user.username,
                "nickname": request.user.nickname,
                "avatar_url": request.user.avatar_url
            }
        }, status=status.HTTP_200_OK)

class UploadAvatarView(APIView):
    authentication_classes = [CustomJWTAuthentication]
    permissions_classes = [IsAuthenticated]

    def post(self, request):
        logger.debug(f"Received upload request from user: {request.user.username}")

        if 'avatar' not in request.FILES:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        file = request.FILES['avatar']
        logger.debug(f"File received: {file.name}, size: {file.size}, content-type: {file.content_type}")

        allowed_types = ['image/jpeg', 'image/png']
        if file.content_type not in allowed_types:
            logger.warning(f"Invalid file type: {file.content_type}")
            return Response({'error': 'Invalid file type. Only JPEG and PNG are allowed'}, status=status.HTTP_400_BAD_REQUEST)

        if file.size > 5 * 1024 * 1024:
            logger.warning(f"File too large: {file.size}")
            return Response({'error': 'File too large. Maximum size is 5MB'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            img = Image.open(file)
            logger.debug(f"Image opened: size: {img.size}, mode: {img.mode}")

            # Resize 500x500
            img.thumbnail((500, 500))
            logger.debug(f"Image resized: new size: {img.size}")

            # For transparent imgs
            if img.mode != 'RGB':
                img = img.convert('RGB')
                logger.debug("Image converted to RGB")

            buffer = io.BytesIO()
            img.save(buffer, format='JPEG')
            buffer.seek(0)
            logger.debug("Image saved to buffer")

            user = request.user
            filename = f"avatar_{user.id}.jpg"
            filepath = f"users/{user.id}/avatar/{filename}"
            logger.debug(f"Preparing to save file: {filepath}")

            # Check if file already exists, if true, deletes it and saves the new one
            if user.avatar:
                logger.debug(f"Deletting old avatar: {user.avatar.name}")
                default_storage.delete(user.avatar.name)

            new_path = default_storage.save(filepath, ContentFile(buffer.read()))
            logger.debug(f"New avatar saved: {new_path}")


            
            #if user.avatar:
            #    old_path = user.avatar.path
            #    if os.path.isfile(old_path):
            #        os.remove(old_path)

            user.avatar = new_path
            user.save()
            logger.debug(f"Avatar updated for user: {user.username}")

            avatar_url = request.build_absolute_uri(user.avatar.url)

            return Response({
                'message': 'Avatar uploaded successfully'}, status=status.HTTP_200_OK)
#                'avatar_url': user.avatar}, status=status.HTTP_200_OK)

        except IOError:
            logger.error(f"IOError while processing image: {str(e)}")
            return Response({'error': 'Unable to process the image'}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Unexpected error while uploading avatar: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GetAvatarView(APIView):
    authentication_classes = [CustomJWTAuthentication]
    permissions_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.avatar:
            return Response({'avatar_url': user.avatar_url}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'No avatar found'}, status=status.HTTP_404_NOT_FOUND)

class UpdateNicknameView(APIView):
    authentication_classes = [CustomJWTAuthentication]
    permissions_classes = [IsAuthenticated]

    def post(self, request):
        nickname = request.data.get('nickname')

        if not nickname:
            return Response({'error': 'Nickname is required'}, status=status.HTTP_400_BAD_REQUEST)

        if len(nickname) > 30:
            return Response({'error': 'Nickname must be 30 characters'}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        user.nickname = nickname
        user.save()

        return Response({'message': 'Nickname updated successfully'}, status=status.HTTP_200_OK)

class GetSelfInfoView(APIView):
    authentication_classes = [CustomJWTAuthentication]
    permissions_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        return Response({
            'nickname': user.nickname
        })
