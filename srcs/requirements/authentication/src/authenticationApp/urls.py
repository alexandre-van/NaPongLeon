from django.urls import path
from .views import UserView, LoginView, LogoutView, UserNicknameView, WebSocketTokenView, TokenRefreshView, UserAvatarView

# for development
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # User management
    path('users/', UserView.as_view(), name='user_create'),
    path('users/me/', UserView.as_view(), name='user_detail'),

    # User profile management
    path('users/me/avatar/', UserAvatarView.as_view(), name='user_avatar'),
    path('users/me/nickname/', UserNicknameView.as_view(), name='update_nickname'),

    # Authentication
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/token/get-access/', WebSocketTokenView.as_view(), name='get_websocket_token'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
