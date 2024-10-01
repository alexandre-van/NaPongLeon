from django.http import JsonResponse
from django.db import transaction
from .models import Game
from .views_auth import auth_required

@auth_required
@transaction.atomic
def matchmaking(request):

    return render(request, "index.html")