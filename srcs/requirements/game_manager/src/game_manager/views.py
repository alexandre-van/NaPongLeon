from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from .utils.decorators import auth_required
from matchmaking.thread import matchmaking_instance
from django.conf import settings
from .utils.logger import logger

@api_view(['GET'])
@auth_required
@transaction.atomic
def get_matchmaking(request, game_mode):
    logger.debug(f'game_mode_request = {game_mode}')
    logger.debug(f'number of players required  = {settings.GAME_MODES.get(game_mode)}')
    return Response({"message": "Matchmaking succeeded"}, status=status.HTTP_200_OK)