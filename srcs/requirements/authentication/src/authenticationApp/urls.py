from django.urls import path
from .views import RegisterView, LoginView, LogoutView, CheckAuthView, UploadAvatarView, GetAvatarView, UpdateNicknameView, GetSelfInfoView, TokenRefreshView

# for development
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('check-auth/', CheckAuthView.as_view(), name='check_auth'),
    path('upload-avatar/', UploadAvatarView.as_view(), name='upload_avatar'),
    path('get-avatar/', GetAvatarView.as_view(), name='get_avatar'),
    path('update-nickname/', UpdateNicknameView.as_view(), name='update_nickname'),
    path('get-self-info/', GetSelfInfoView.as_view(), name='get_self_info'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh')
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
