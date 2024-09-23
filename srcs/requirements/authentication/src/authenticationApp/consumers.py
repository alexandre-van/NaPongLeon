import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import CustomUser, Notification
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from jwt import decode as jwt_decode
from django.conf import settings

class FriendRequestConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = await self.get_user_from_token()
        logger.debug('Connection attempt')
        if not self.user:
            logger.debug('No user, no connection')
            await self.close()
        else:
            logger.debug('Trying to add to group')
            await self.channel_layer.group_add(
                f"user_{self.user.id}",
                self.channel_name
            )
            await self.accept()
            logger.debug('Connection accepted')

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

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')

        action_handlers = {
            'send_request': self.send_friend_request,
            'accept_request': self.accept_friend_request,
            'reject_request': self.reject_friend_request,
            'mark_as_read': self.mark_notification_as_read,
            'delete_request':
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

    async def send_friend_request(self, target_user_id):
        try:
            target_user, notification = await self._send_friend_request_and_notify(target_user_id)

            # Send notification to target user
            await self.channel_layer.group.send(
                f"user_{target_user.id}",
                {
                    "type": "friend_request_received",
                    "user": {
                        "id": self.user.id,
                        "username": self.user.username,
                    },
                    "notification": notification
                }
            )

            # Inform success to the sender
            await self.send(text_data=json.dumps({
                'type': 'friend_request_sent',
                'message': f'Friend request sent to {target_user.username}'
                    'success': True
            }))

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
    def _send_friend_request_and_notify(self, target_user_id):
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
        return target_user, notification.to_dict()



    @database_sync_to_async
    def _accept_friend_request_and_notify(self, target_user_id):
        from_user = CustomUser.objects.get(id=target_user_id)
        self.user.accept_friend_request(from_user)

        notification = Notification.objects.create(
            user=from_user,
            content=f"{self.user.username} has accepted your friend request",
            notification_type="friend_request_accepted"
        )

        await self.channel_layer.group.send(
            f"user_{from_user.id}",
            {
                "type": "friend_request_accepted",
                "user": {
                    "id": self.user.id,
                    "username": self.user.username,
                },
                "notification": notification.to_dict()
            }
        )
        return from_user

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
