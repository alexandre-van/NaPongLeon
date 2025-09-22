from .utils.httpResponse import HttpResponseJD, HttpResponseBadRequestJD, HttpResponseJDexception
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from .services.FriendRequestService import FriendRequestService
from asgiref.sync import sync_to_async
from .models import CustomUser
from rest_framework_simplejwt.tokens import AccessToken
from .serializers import UserSerializer
from rest_framework import serializers

# for LoginView and Setup2FAView
from django_otp import user_has_device

import json
import logging
logger = logging.getLogger(__name__)

async def LoginView(request):
    from django.contrib.auth import authenticate, logout
    from .utils.two_factor_auth import create_login_response
    from datetime import timedelta
    from django.utils import timezone

    if request.method != 'POST':
        return HttpResponseBadRequestJD('Method not allowed')

    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
    except json.JSONDecodeError:
        return HttpResponseJD('Invalid JSON', 400)

    user = await database_sync_to_async(authenticate)(username=username, password=password)

    if user is None:
        return HttpResponseJD('Invalid credentials', 401)
    
    has_2fa = await database_sync_to_async(user_has_device)(user)
    if not has_2fa:
        return await create_login_response(user, request)
    
    temp_token = AccessToken()
    temp_token['type'] = '2fa_pending'
    temp_token['user_id'] = user.id
    temp_token.set_exp(from_time=timezone.now(), lifetime=timedelta(minutes=5))

    await database_sync_to_async(logout)(request)

    return HttpResponseJD('2FA required', 200, {
        'requires_2fa': True,
        'temp_token': str(temp_token)
    })

async def Login2FAView(request):
    from .utils.two_factor_auth import create_login_response, validate_totp

    if request.method != 'POST':
        return HttpResponseBadRequestJD('Method not allowed')

    try:
        data = json.loads(request.body)
        totp_token = data.get('code')
        temp_token = data.get('temp_token')

        if not temp_token:
            return HttpResponseBadRequestJD('Missing fields')
        if not totp_token:
            return HttpResponseJD('2FA token required', 403)

        try:
            token = AccessToken(temp_token)
            if token['type'] != '2fa_pending':
                return HttpResponseJD('Invalid token type', 401)

            user = await database_sync_to_async(CustomUser.objects.get)(id=token['user_id'])
        except :
            return HttpResponseJD('Invalid or expired token', 401)

        is_valid = await validate_totp(user, totp_token)
        if not is_valid:
            return HttpResponseJD('Invalid 2FA token', 401)
    except json.JSONDecodeError:
        return HttpResponseJD('Invalid JSON', 400)

    return await create_login_response(user, request)



async def Setup2FAView(request):
    user = request.user
    if not user.is_authenticated:
        return HttpResponseJD('Authentication required', 401)
    
    if user:
        username = user.username
        if '_42' in username:
            return HttpResponseJD('Users from 42 cannot have 2FA', 401)

    # Give QR code
    if request.method == 'GET':
        from .utils.two_factor_auth import setup_2fa

        user_has_2fa = await database_sync_to_async(user_has_device)(user)
        if user_has_2fa:
            return HttpResponseJD('2FA setup already setup', 200)
        
        config_url = await setup_2fa(user)
        return HttpResponseJD('2FA setup initiated', 200, {
            'config_url': config_url,
            'secret_key': config_url.split('secret=')[1].split('&')[0]
        })
    
    # Register device
    if request.method == 'POST':
        try:
            from django_otp.plugins.otp_totp.models import TOTPDevice

            data = json.loads(request.body)
            token = data.get('token')

            if not token:
                return HttpResponseBadRequestJD('Token required')

            @sync_to_async
            def verify_token():
                devices = TOTPDevice.objects.filter(user=user, confirmed=False)
                if devices:
                    device = devices[0]
                    if device.verify_token(token):
                        device.confirmed = True
                        device.save()
                        return True
                return False

            if await verify_token():
                return HttpResponseJD('2FA setup successful', 200)
            return HttpResponseJD('Invalid token', 400)
        
        except json.JSONDecodeError:
            return HttpResponseBadRequestJD('Invalid JSON')



async def LogoutView(request):
    if request.method != 'POST':
        return HttpResponseJD('Method not allowed', 405)
    user = request.user
    if user.is_authenticated:
        response = HttpResponseJD('Logout successuful', 200)
        response.delete_cookie(
            'access_token',
        )
        response.delete_cookie(
            'refresh_token',
        )
        response.delete_cookie(
            'csrftoken',
        )
        return response
    return HttpResponseBadRequestJD('Anonymous user')



async def UserNicknameView(request):
    if request.method != 'PATCH':
        return HttpResponseJD('Method not allowed', 405)

    try:
        data = json.loads(request.body)
        nickname = data.get('nickname')

        serializer = UserSerializer()
        await database_sync_to_async(serializer.validate_nickname)(nickname)

        user = request.user
        if user.is_authenticated:
            await user.update_nickname(nickname)
            data = {
                'nickname': nickname
            }
            return HttpResponseJD('Nickname updated', 200, data)
    except json.JSONDecodeError:
        return HttpResponseBadRequestJD('Invalid JSON')
    except serializers.ValidationError as e:
        return HttpResponseJD('Invalid Nickname', 400, {'errors': e.detail})
    except Exception as e:
            return HttpResponseBadRequestJD(f"{e}")
    return HttpResponseBadRequestJD('Anonymous user')

async def UserAvatarView(request):
    from django.core.files.base import ContentFile
    from django.core.files.storage import default_storage

    user = request.user
    if request.method == 'GET':
        if user.avatar:
            data = {
                'avatar_url': user.avatar.url
            }
            return HttpResponseJD('Avatar found', 200, data)
        else:
            return HttpResponseJD('No avatar found', 404)
    elif request.method == 'POST':
        if 'avatar' not in request.FILES:
            return HttpResponseBadRequestJD('No file uploaded')

        file = request.FILES['avatar']
        allowed_types = ['image/jpeg', 'image/png']
        if file.content_type not in allowed_types:
            return HttpResponseBadRequestJD('Invalid file type. Only JPEG and PNG are allowed.')

        if file.size > 1024 * 1024:
            return HttpResponseBadRequestJD('File too large. Maximum size is 1MB')
        
        try:
            from .utils.image_process import process_image
            img_content = file.read()
            buffer = await sync_to_async(process_image)(img_content)

            filename = f"avatar_{user.id}.jpg"
            filepath = f"users/{user.id}/avatar/{filename}"

            # Check if file already exists, if true, deletes it and saves the new one
            if user.avatar:
                await sync_to_async(default_storage.delete)(user.avatar.name)
            new_path = await sync_to_async(default_storage.save)(filepath, ContentFile(buffer.getvalue()))
            await user.update_avatar_url(new_path)

            return HttpResponseJD('Avatar uploaded successfully', 200)
            
        except IOError:
            return HttpResponseBadRequestJD('Unable to process the image')

        except Exception as e:
            return HttpResponseJDexception(e)
    else:
        return HttpResponseJD('Method not allowed', 405)



async def FriendsRequestView(request):
    user = await sync_to_async(lambda: request.user)()
    body = request.body
    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        return HttpResponseBadRequestJD('Invalid JSON')
    
    if request.method == "GET":
    # Get waiting requests
        return HttpResponseJD('Get method not implemented yet', 501)

    elif request.method == "POST":
    # Send a friend request
        receiver_username = data.get('target_user')
        if not receiver_username:
            return HttpResponseBadRequestJD('Username needed')
        try:
            from .models import CustomUser

            receiver = await sync_to_async(CustomUser.objects.get)(username=receiver_username)
        except CustomUser.DoesNotExist:
            return HttpResponseJD('Target user does not exist', 404)
        if user == receiver:
            return HttpResponseBadRequestJD('Cannot be yourself')

        try:
            result = await FriendRequestService.create_and_send_friend_request(user, receiver)
            if result:
                return HttpResponseJD('Friend request sent', 201)
            else:
                return HttpResponseJD('Friend request already exists', 409)
        except Exception as e:
            return HttpResponseJDexception(e)

    elif request.method == "PATCH":
    # Accept a friend request
        notification_id = data.get('notificationId')
        if not notification_id:
            return HttpResponseBadRequestJD('Notification id needed')

        try:
            result = await FriendRequestService.accept_friend_request(user, notification_id)
            if result:
                return HttpResponseJD('Friend request accepted', 200)
            else:
                return HttpResponseJD('Friend request not found', 404)
        except Exception as e:
            return HttpResponseJDexception(e)

    elif request.method == "DELETE":
    # Refuse a friend request
        notification_id = data.get('id')
        if not notification_id:
             return HttpResponseBadRequestJD('Notification id needed')

        try:
            result = await FriendRequestService.reject_friend_request(user, notification_id)
            if result:
                return HttpResponseJD('Friend request rejected', 200)
            else:
                return HttpResponseJD('Friend request not found', 404)
        except Exception as e:
            return HttpResponseJDexception(e)

    else: 
        return HttpResponseJD('Method not allowed', 405)



async def FriendsView(request):
    user = await sync_to_async(lambda: request.user)()
    if not user or not user.is_authenticated:
        return HttpResponseJD('Authentication required', 401)

    if request.method == 'DELETE':
        # Delete a friend from the list
        from .models import CustomUser

        body = request.body
        friend_id = json.loads(body).get('friendId')

        if not friend_id:
            return HttpResponseBadRequestJD('Friend id needed')

        try:
            friend = await sync_to_async(CustomUser.objects.get)(id=friend_id)
            if friend is None:
                return HttpResponseJD('No user found', 404)

            result = await user.remove_friend_from_list(friend)
            if result:
                await FriendRequestService.delete_self_from_ex_friend_list(user, friend_id)
                return HttpResponseJD('Removed friend successfully', 200)
            return HttpResponseJD('Friend to remove not found', 404)

        except Exception as e:
            return HttpResponseJDexception(e)

    else:
        return HttpResponseJD('Method not allowed', 405)



async def NotificationsView(request):
    from .models import Notification

    user = await sync_to_async(lambda: request.user)()
    if request.method == "GET":
        notifications = await Notification.get_all_received_notifications(user)

        for notification in notifications:
            notification['created_at'] = notification['created_at'].isoformat()

        response = HttpResponseJD('Notifications', 200, notifications)
        return response


    # Delete specific notification
    elif request.method == "DELETE":
        body = request.body
        notification_id = json.loads(body).get('id')

        if not notification_id:
            return HttpResponseBadRequestJD('Notification id needed')

        try:
#            result = await database_sync_to_async(Notification.objects.get(id=notification_id).delete)()
            result = await Notification.delete_notification(notification_id)
            if result:
                return HttpResponseJD('Notification deleted', 200)
            else:
                return HttpResponseJD('Notification not found', 404)

        except Exception as e:
            return HttpResponseJDexception(e)

    else:
        return HttpResponseJD('Method not allowed', 405)

async def WebSocketTokenView(request):
    from rest_framework_simplejwt.tokens import AccessToken

    if request.method == "GET":
        token = AccessToken.for_user(request.user)
        #return Response({'token': str(token)})
        return HttpResponseJD('Access Token provided', 200, { 'token': str(token) })
    return HttpResponseJD('Method not allowed', 405)



async def VerifyFriendsView(request):
    user = await sync_to_async(lambda: request.user)
    if user == AnonymousUser:
        return HttpResponseJD('Unknown user', 401)
    


async def PasswordResetView(request):
    from django.contrib.auth.tokens import default_token_generator
    from django.core.mail import send_mail
    from django.template.loader import render_to_string
    from django.utils.encoding import force_bytes
    from django.utils.http import urlsafe_base64_encode
    from django.urls import reverse
    import os
    from django.conf import settings

    if request.method != 'POST':
        return HttpResponseJD('Method not allowed', 405)

    try:
        data = json.loads(request.body)
        email = data.get('email')

        try:
            user = await database_sync_to_async(CustomUser.objects.get)(email=email)
        except CustomUser.DoesNotExist:
            return HttpResponseJD('If this email address exists, you will receive the password reset instructions', 200)
        
        token = await database_sync_to_async(default_token_generator.make_token)(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        reset_url = f"{settings.SITE_URL}/reset-password/{uid}/{token}"
        logger.debug(f"reset_url={reset_url}")
        context = {
            'user': user,
            'reset_url': reset_url,
        }


        template_name = 'authenticationApp/password_reset_email.html'
        
        # Try to list template directory contents
        template_dir = '/app/authenticationApp/templates/authenticationApp'
        if os.path.exists(template_dir):
            logger.debug(f"Template directory contents: {os.listdir(template_dir)}")
        else:
            logger.debug(f"Template directory does not exist: {template_dir}")

        try:
            email_html = render_to_string(template_name, context)
            logger.debug("Successfully rendered email template")
        except Exception as template_error:
            logger.error(f"Template rendering error: {str(template_error)}")
            raise

        email_subject = 'Reinitiatize your password'

        await database_sync_to_async(send_mail)(
            subject=email_subject,
            message=email_html,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email],
            html_message=email_html,
            fail_silently=False,
        )

        return HttpResponseJD('If this email address exists, you will receive the password reset instructions', 200)

    except Exception as e:
        logger.error(f"Erreur lors du rendu du template: {str(e)}")
        logger.error(f"Template dirs: {settings.TEMPLATES[0]['DIRS']}")
        logger.error(f"App Dirs enabled: {settings.TEMPLATES[0]['APP_DIRS']}")
        return HttpResponseJDexception(e)



async def PasswordResetConfirmationView(request, uidb64, token):
    from django.contrib.auth.tokens import default_token_generator
    from django.utils.http import urlsafe_base64_decode

    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = await database_sync_to_async(CustomUser.objects.get)(pk=uid)
        is_token_valid = await database_sync_to_async(default_token_generator.check_token)(user, token)

        if is_token_valid:
            if request.method == 'POST':
                try:
                    data = json.loads(request.body)
                    new_password = data.get('new_password')

                    serializer = UserSerializer()
                    try:
                        await database_sync_to_async(serializer.validate_password)(new_password)
                    except serializers.ValidationError as e:
                        return HttpResponseJD('Password validation failed', 400, {'errors': e.detail})

                    await database_sync_to_async(user.set_password)(new_password)
                    await database_sync_to_async(lambda: user.save(update_fields=['password']))()
                    return HttpResponseJD('Password modified', 200)
                
                except json.JSONDecodeError:
                    return HttpResponseBadRequestJD('Invalid JSON')

            else:
                return HttpResponseJD('Invalid Token', 200)

        else:
            return HttpResponseJD('Invalid or expired Token', 400)

    
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        return HttpResponseJD('Could not reset password', 403)



async def TokenRefreshView(request):
    if request.method != 'GET':
        return HttpResponseJD('Method not allowed', 405)

    refresh_token = request.COOKIES.get('refresh_token')
    if not refresh_token:
        return HttpResponseJD('No refresh token provided', 401)

    try:
        from rest_framework_simplejwt.tokens import RefreshToken
        from datetime import timedelta
        from django.utils import timezone

        refresh = RefreshToken(refresh_token)
        
        # Créer un nouveau access token avec une durée de 5 minutes
        access_token = refresh.access_token
        access_token.set_exp(from_time=timezone.now(), lifetime=timedelta(minutes=5))

        response = HttpResponseJD('Token refreshed', 200)
        response.set_cookie(
            'access_token',
            str(access_token),
            httponly=True,
            secure=False,  # True for production
            samesite='Strict',
            max_age=300  # 5 minutes
        )
        return response

    except Exception as e:
        return HttpResponseJD('Invalid refresh token', 401)