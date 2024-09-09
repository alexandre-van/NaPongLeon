#from django.shortcuts import render
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserSerializer

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
        #logger.info("Received registration request")
        #logger.debug(f"Request data: {request.data}")
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

class CheckAuthView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "IsAuthenticated": True,
            "username": request.user.username,
            "userId": request.user.id
        })
