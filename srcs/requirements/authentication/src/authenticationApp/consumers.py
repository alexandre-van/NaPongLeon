import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from .models import CustomUser, Notification
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from jwt import decode as jwt_decode
from django.conf import settings

import logging
logger = logging.getLogger(__name__)

class FriendRequestConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        logger.debug(f'Connection attempt, scope[user]={self.scope["user"]}')
#        self.user = await self.get_user_from_token()
        self.user = self.scope["user"]
        logger.debug(f'\n-------------------------------------CONNECTION WEBSOCKET\n\n\nself.user: {self.user}\n')
        if not self.user:
            logger.debug('No user, no connection')
            await self.close()
        else:
            logger.debug('channel_layer user_')
            logger.debug(self.user.id)

            await self.channel_layer.group_add(
                f"user_{self.user.id}",
                self.channel_name
            )
            await self.accept()
            await self.user.update_user_status(True)
            await self.send_status_friends(True)
            logger.debug('Connection accepted')

    '''
    @database_sync_to_async
    def get_user_from_token(self):
        token = self.scope['cookies'].get('access_token')
        if not token:
            return None
        try:
            UntypedToken(token)
        except (InvalidToken, TokenError):
            return None

        decoded_data = jwt_decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = decoded_data['user_id']
        CustomUser = get_user_model()
        return CustomUser.objects.get(id=user_id)
    '''

    async def disconnect(self, close_code):
        from django_otp import devices_for_user
        from django_otp.plugins.otp_totp.models import TOTPDevice
        from asgiref.sync import sync_to_async

        await self.user.update_user_status(False)
        await self.send_status_friends(False)

        @sync_to_async
        def delete_unconfirmed_2fa_auth(user):
            for device in devices_for_user(user, confirmed=False):
                device.delete()
                return True
            return False
        
        result = await delete_unconfirmed_2fa_auth(self.user)
        logger.debug(f"\n\nconsumers delete_unconfirmed_2fa_auth : {result}\n")



    async def receive(self, text_data):
        logger.debug('receive debut')
        data = json.loads(text_data)
        action = data.get('action')

        action_handlers = {
            'send_request': self.send_friend_request,
            'accept_request': self.accept_friend_request,
            'reject_request': self.reject_friend_request,
            'mark_as_read': self.mark_notification_as_read,
#            'delete_request': 
        }

        handler = action_handlers.get(action)
        if handler:
            if action == 'mark_as_read':
                await handler(data.get('notification_id'))
            else:
                await handler(data.get('target_user_id'))
        else:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'Unknown action: {action}'
            }))
        logger.debug('receive end')


        
    async def send_status_friends(self, status):
        friends = await self.user.aget_friends()
        for friend in friends:
            logger.debug(f"friend = {friend}")
            await self.channel_layer.group_send(
                f"user_{friend['id']}",
                {
                    "type": "friend_status",
                    "friend": self.user.username,
                    "status": status
                }
            )

    async def send_friend_request(self, target_user_id):
        try:
            target_user, notification = await self._send_friend_request_and_create_notification(target_user_id)

            # Send notification to target user
            logger.debug(notification.user.id)
            logger.debug('hello')
            await self.channel_layer.group_send(
                f"user_{notification.user.id}",
                notification.to_group_send_format()
            )

            # Inform success to the sender
            await self.send(text_data=json.dumps({
                'type': 'friend_request_sent',
                'message': f'Friend request sent to {target_user.username}',
                'success': True
            }))
            logger.debug('send_friend_request end')

        except ObjectDoesNotExist as e:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': str(e),
                'success': False
            }))
        except ValueError as e:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': str(e),
                'success': False
            }))

    @database_sync_to_async
    def _send_friend_request_and_create_notification(self, target_user_id):
        logger.debug('_send_friend_request_and_create_notification debut')
        target_user = CustomUser.objects.get(id=target_user_id)
        if target_user is None:
            raise ObjectDoesNotExist("Target user does not exist")

        friendship = self.user.send_friend_request(target_user)
        if not friendship:
            raise ValueError("Friend request could not be sent")
        notification = Notification.objects.create(
            user=target_user,
            content=f"{self.user.username} sent you a friend request",
            notification_type="friend_request_received"
        )
        return target_user, notification




    async def accept_friend_request(self, from_user_id):
        try:
            from_user, notification = await self._accept_friend_request_and_create_notification(self, from_user_id)

            await self.channel_layer.group_send(
            f"user_{target_user.id}",
            {
                "type": "friend_request_accepted",
                "user": {
                    "id": self.user.id,
                    "username": self.user.username,
                },
                "notification": notification
            }
        )
        
        except ObjectDoesNotExist as e:
            await self.send(text_data=json.dumps({
                'type': error,
                'message': str(e),
                'success': False
            }))

        except ValueError as e:
            await self.send(text_data=json.dumps({
                'type': error,
                'message': str(e),
                'success': False
            }))

    @database_sync_to_async
    def _accept_friend_request_and_create_notification(self, from_user_id):
        from_user = CustomUser.objects.get(id=from_user_id)
        if target_user is None:
            raise ObjectDoesNotExist("Target user does not exist")

        friendship = self.user.accept_friend_request(from_user)
        if not friendship:
            raise ValueError("Accept friend request could not be sent")

        notification = Notification.objects.create(
            user=from_user,
            content=f"{self.user.username} has accepted your friend request",
            notification_type="friend_request_accepted"
        )

        return from_user, notification.to_dict()

    @database_sync_to_async
    def reject_friend_request(self, target_user_id):
        from_user = CustomUser.objects.get(id=target_user_id)
        self.user.reject_friend_request(from_user)
        return from_user

    @database_sync_to_async
    def mark_notification_as_read(self, notification_id):
        notification = Notification.objects.get(id=notification_id, user=self.user)
        notification.mark_as_read()


    # Types of notification

    async def friend_request_accepted(self, event):
        await self.send(text_data=json.dumps({
            'type': 'friend_request_accepted',
            'user': event['user'],
            'notification': event['notification']
        }))

    # TO DO a refactoriser directement dans la methode d'appel
    async def friend_request_rejected(self, event):
        await self.send(text_data=json.dumps({
            'type': 'friend_request_rejected',
            'user': event['user']
        }))

    async def friend_request_received(self, event):
        await self.send(text_data=json.dumps({
            'type': 'friend_request_received',
            'user': event['user']
        }))

    async def notification(self, event):
        await self.send(text_data=json.dumps(event['notification']))

    async def friend_status(self, event):
        await self.send(text_data=json.dumps({
            "type": "friend_status",
            "friend": event["friend"],
            "status": event["status"]
        }))