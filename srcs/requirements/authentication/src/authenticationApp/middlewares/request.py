
from authenticationApp.models import CustomUser
import logging
logger = logging.getLogger(__name__)

class DjangoUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        asgi_user = request.META.get('HTTP_ASGI_USER')
        if asgi_user:
            try:
                request.user = CustomUser.objects.get(username=asgi_user)
            except CustomUser.DoesNotExist:
                pass
        response = self.get_response(request)
        return response