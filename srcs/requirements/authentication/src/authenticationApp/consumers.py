import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import CustomUser, Notification
import logging
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



    async def disconnect(self):
        from django_otp import devices_for_user
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

    @database_sync_to_async
    def update_user_status(self, is_online):
        self.user.update_user_status(is_online)

    @database_sync_to_async
    def get_user(self):
        return CustomUser.objects.get(id=self.user_id)

    # Types of notification

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