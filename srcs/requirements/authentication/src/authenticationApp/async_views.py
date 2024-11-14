from .utils.httpResponse import HttpResponseJD, HttpResponseBadRequestJD, HttpResponseJDexception
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
#from rest_framework import status
from asgiref.sync import sync_to_async

import json
import logging
logger = logging.getLogger(__name__)

async def LoginView(request):
    from django.contrib.auth import authenticate
    from django_otp import user_has_device
    from .utils.two_factor_auth import create_login_response, validate_totp

    if request.method != 'POST':
        return HttpResponseBadRequestJD('Method not allowed')

    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        totp_token = data.get('totpToken') # Optional 2FA token
        logger.debug(f'data:{data}')
    except json.JSONDecodeError:
        return HttpResponseJD('Invalid JSON', 400)

    user = await database_sync_to_async(authenticate)(username=username, password=password)


    if user is None:
        return HttpResponseJD('Invalid credentials', 401)
    
    has_2fa = await database_sync_to_async(user_has_device)(user)
    if not has_2fa:
        return await create_login_response(user, request)

    logger.debug(f'totp_token={totp_token}')
    # If 2FA enabled but no token provided
    if not totp_token:
        logger.debug('not totp_token')
        return HttpResponseJD('2FA token required', 403, {'requires_2fa': True})

    is_valid = await validate_totp(user, totp_token)
    if not is_valid:
        return HttpResponseJD('Invalid 2FA token', 401)

    return await create_login_response(user, request)



async def Setup2FAView(request):
    if not request.user.is_authenticated:
        return HttpResponseJD('Authentication required', 401)

    # Give QR code
    if request.method == 'GET':
        from .utils.two_factor_auth import setup_2fa

        device, config_url = await setup_2fa(request.user)
        return HttpResponseJD('2FA setup initiated', 200, {
            'config_url': config_url,
            'secret_key': device.config_url.split('secret=')[1].split('&')[0]
        })
    
    # Register device
    if request.method == 'POST':
        try:
            from django.db import transaction
            from django_otp.plugins.otp_totp.models import TOTPDevice

            data = json.loads(request.body)
            token = data.get('token')

            if not token:
                return HttpResponseBadRequestJD('Token required')

            @sync_to_async
            def verify_token():
                with transaction.atomic():
                    devices = TOTPDevice.objects.filter(user=request.user, confirmed=False)
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
    logger.debug(f"request:{request}")
    logger.debug(f"request.user:{request.user}")
    if request.method != 'PATCH':
        return HttpResponseJD('Method not allowed', 405)

    try:
        data = json.loads(request.body)
        nickname = data.get('nickname')
    except json.JSONDecodeError:
        return HttpResponseBadRequestJD('Invalid JSON')

    user = request.user
    logger.debug(f"user:{user}")
    logger.debug(f"user.is_authenticated ={user.is_authenticated}")
    if user.is_authenticated:
        await user.update_nickname(nickname)
        data = {
            'nickname': nickname
        }
        return HttpResponseJD('Nickname updated', 200, data)
    return HttpResponseBadRequestJD('Anonymous user')

async def UserAvatarView(request):
    from django.core.files.base import ContentFile
    from django.core.files.storage import default_storage

    user = request.user
    if request.method == 'GET':
        if user.avatar:
            logger.debug(f"Avatar_url: {user.avatar.url}")
            data = {
                'avatar_url': user.avatar.url
            }
            return HttpResponseJD('Avatar found', 200, data)
        else:
            logger.debug("No avatar found")
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
            from .services.FriendRequestService import FriendRequestService

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
            from .services.FriendRequestService import FriendRequestService

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
            from .services.FriendRequestService import FriendRequestService

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

    if request.method == 'GET':
        # Get all friends
        friends = await user.aget_friends()

        if friends:
            return HttpResponseJD('Friends', 200, friends)
        return HttpResponseJD('Friends not found', 404)

    elif request.method == 'DELETE':
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
                return HttpResponseJD('Removed friend successfully', 200)
            return HttpResponseJD('Friend to remove not found', 404)

        except Exception as e:
            return HttpResponseJDexception(e)

    else:
        return HttpResponseJD('Method not allowed', 405)



async def NotificationsView(request):
    from .models import Notification

    logger.debug(f"request.method: {request.method}")
    user = await sync_to_async(lambda: request.user)()
    if request.method == "GET":
        notifications = await Notification.get_all_received_notifications(user)

        for notification in notifications:
            notification['created_at'] = notification['created_at'].isoformat()

        logger.debug(f"notifications={notifications}")
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
    if request.method == "GET":
        logger.debug(f"\n\n\n WEBSOCKETTOKENVIEW request.user={request.user}")
        token = AccessToken.for_user(request.user)
        #return Response({'token': str(token)})
        return HttpResponseJD('Token ', 200)
    return HttpResponseJD('Method not allowed', 405)
