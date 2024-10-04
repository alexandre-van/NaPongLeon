from django.urls import path
from .views import UserView, UserAvatarView#, UserNicknameView, WebSocketTokenView, TokenRefreshView, UserAvatarView, FriendsView, FriendsRequestView
from .async_views import LoginView, LogoutView, UserNicknameView

# for development
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # User management
    path('users/', UserView.as_view(), name='user_create'),
    path('users/me/', UserView.as_view(), name='user_detail'),

    # User profile management
    path('users/me/avatar/', UserAvatarView.as_view(), name='user_avatar'),
    path('users/me/nickname/', UserNicknameView, name='update_nickname'),

    # Authentication
    path('auth/login/', LoginView, name='login'),
    path('auth/logout/', LogoutView, name='logout'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

'''
    path('auth/token/get-access/', WebSocketTokenView.as_view(), name='get_websocket_token'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Friends
    path('friends/', FriendsView.as_view(), name='friends'),
    path('friends/requests/', FriendsRequestView, name='friends_requests'),

    path('auth/login/', AsyncLoginConsumer.as_asgi(), name='login'),
    path('users/me/nickname/', UserNicknameView.as_asgi(), name='update_nickname'),
    '''


