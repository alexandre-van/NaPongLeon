from rest_framework.permissions import IsAuthenticated
from asgiref.sync import sync_to_async

class AsyncIsAuthenticated(IsAuthenticated):
    async def has_permission(self, request, view):
        return await sync_to_async(super().has_permission)(request, view)
