
from authenticationApp.models import CustomUser
import logging
logger = logging.getLogger(__name__)

class DjangoUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
#        (f"DjangoUserMiddleware: request={request}")
        asgi_user = request.META.get('HTTP_ASGI_USER')
 #       (f"DjangoUserMiddleware: request.META={request.META}\nasgi_user={asgi_user}")
        if asgi_user:
            try:
                request.user = CustomUser.objects.get(username=asgi_user)
                (f"request.user={request.user}")
            except CustomUser.DoesNotExist:
                pass
        response = self.get_response(request)
  #      (f"DjangoUserMiddleware: response={response}")
        return response