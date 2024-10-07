from rest_framework.permissions import IsAuthenticated
from authenticationApp.auth_middleware import CustomJWTAuthentication
from asgiref.sync import sync_to_async

class AsyncCustomJWTAuthentication(CustomJWTAuthentication):
    async def authenticate(self, request):
        return await sync_to_async(super().authenticate)(request)

class AsyncIsAuthenticated(IsAuthenticated):
    async def has_permission(self, request, view):
        return await sync_to_async(super().has_permission)(request, view)
