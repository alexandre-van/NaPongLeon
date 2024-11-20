
from authenticationApp.models import CustomUser
import logging
logger = logging.getLogger(__name__)

class DjangoUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
#        logger.debug(f"DjangoUserMiddleware: request={request}")
        asgi_user = request.META.get('HTTP_ASGI_USER')
 #       logger.debug(f"DjangoUserMiddleware: request.META={request.META}\nasgi_user={asgi_user}")
        if asgi_user:
            try:
                request.user = CustomUser.objects.get(username=asgi_user)
                logger.debug(f"request.user={request.user}")
            except CustomUser.DoesNotExist:
                pass
        response = self.get_response(request)
  #      logger.debug(f"DjangoUserMiddleware: response={response}")
        return response