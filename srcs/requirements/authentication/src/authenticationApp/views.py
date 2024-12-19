from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from .utils.httpResponse import HttpResponseJD, HttpResponseBadRequestJD, HttpResponseNotFoundJD, HttpResponseJDexception
from .serializers import UserSerializer, FriendshipSerializer
from authenticationApp.auth_middleware import CustomJWTAuthentication
#from .async_views import AsyncLoginConsumer

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
        logger.debug('\nUserView POST\n')
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            logger.debug(f'request.data = {request.data}')
            return Response({'message': 'Registration success'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Get User info
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response({
            "user": serializer.data
        }, status=status.HTTP_200_OK)
    


class VerifyTokenView(APIView):
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated]


    def post(self, request):
        #logger.debug(f"request.data: {request.data}")
        user = request.user
        logger.debug('\n\n\n\n\nVerifyTokenView\n\n\n\n\n')
        logger.debug(f"user={user}")
        logger.debug(f"username={user.username}")
        logger.debug(f"nickname: {user.nickname}")
        return Response({
            'user': user.username,
            'nickname': user.nickname
        }, status=status.HTTP_200_OK)
        #token = request.token
        #access_ authenticate(request.token.get('access_token'))