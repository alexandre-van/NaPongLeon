import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.core.exceptions import ObjectDoesNotExist
from .models import CustomUser, Notification
from django.db import transaction
import logging
import asyncio
logger = logging.getLogger(__name__)

class FriendRequestConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope.get("user", None).id
        self.user = await self.get_user()
        if not self.user:
            await self.close()
        else:

            await self.accept()
            await self.channel_layer.group_add(
                f"user_{self.user.id}",
                self.channel_name
            )
            await self.update_user_status(True)
            await self.send_status_friends(True)
            notifications = await Notification.get_all_notifications(self.user)
            for notification in notifications:
                await self.send(text_data=json.dumps(notification.to_dict()))
            logger.debug('Connection accepted')




    async def disconnect(self, close_code):
        from django_otp import devices_for_user
        from django_otp.plugins.otp_totp.models import TOTPDevice
        from asgiref.sync import sync_to_async
        self.user = await self.get_user()

        try:
            if self.user and self.user.is_authenticated:
                await self.update_user_status(False)
                await self.send_status_friends(False)

            @sync_to_async
            def delete_unconfirmed_2fa_auth(user):
                for device in devices_for_user(user, confirmed=False):
                    device.delete()
                    return True
                return False

            result = await delete_unconfirmed_2fa_auth(self.user)
        except Exception as e:
            logger.error(f"Error during disconnect: {str(e)}")

    async def receive(self, text_data):
        self.user = await self.get_user()
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


        
    async def send_status_friends(self, status):
        self.user = await self.get_user()
        friends = await self.user.aget_friends()
        for friend in friends:

            await self.channel_layer.group_send(
                f"user_{friend['id']}",
                {
                    "type": "friend_status",
                    "friend": self.user.username,
                    "status": status
                }
            )

    async def send_friend_request(self, target_user_id):
        self.user = await self.get_user()
        try:
            target_user, notification = await self._send_friend_request_and_create_notification(target_user_id)

            # Send notification to target user
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
        self.user = await self.get_user()
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
    def update_user_status(self, is_online):
        self.user.update_user_status(is_online)

    @database_sync_to_async
    def get_user(self):
        return CustomUser.objects.get(id=self.user_id)

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
        self.user = await self.get_user()
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
    
    async def friend_list_user_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'friend_list_user_update',
            'user': event['user'],
        }))

    async def friend_deleted(self, event):
        await self.send(text_data=json.dumps({
            'type': 'friend_deleted',
            'friend_id': event['friend_id'],
        }))