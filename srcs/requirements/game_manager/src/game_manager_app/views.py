from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from .views_auth import auth_required

@api_view(['GET'])
@auth_required
@transaction.atomic
def matchmaking(request):
    
    return Response({"message": "Matchmaking succeeded"}, status=status.HTTP_200_OK)