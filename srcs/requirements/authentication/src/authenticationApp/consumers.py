import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
from .models import CustomUser, Notification
import logging
logger = logging.getLogger(__name__)

class FriendRequestConsumer(AsyncWebsocketConsumer):
    '''
    async def connect(self):
        self.user_id = self.scope.get("user", None).id
        logger.debug(f'connect self.user_id')

        if not self.user:
            logger.debug(f'anonymous du coup')
            await self.close()
        else:
            logger.debug(f'else du coup')
            self.user = await self.get_user()
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
            friends = await self.user.aget_friends()
            logger.debug(f'Consumer, friends: ${friends}')
            logger.debug(f'self.user: ${self.user}')
            for friend in friends:
                await self.send_user_info(self.user.id, friend)
            #    pass

    
    async def disconnect(self, close_code):
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
    '''

    async def connect(self):
        # First, get the user from scope
        user = self.scope.get("user", None)
        
        # Check if we have a valid user
        if not user or not user.id:
            logger.debug('Anonymous user, closing connection')
            await self.close()
            return
            
        # Store user_id and initialize user only if we have a valid user
        self.user_id = user.id
        logger.debug(f'Connected with user_id: {self.user_id}')
        
        # Get the full user object from database
        self.user = await self.get_user()
        
        # Accept the connection and set up the channel
        await self.accept()
        await self.channel_layer.group_add(
            f"user_{self.user.id}",
            self.channel_name
        )
        
        # Initialize user status and send notifications
        await self.update_user_status(True)
        await self.send_status_friends(True)
        
        # Send existing notifications
        notifications = await Notification.get_all_notifications(self.user)
        for notification in notifications:
            logger.debug(f'Boucle for, notification: {notification}')
            await self.send(text_data=json.dumps(notification.to_dict()))
            
        # Send friends information
        friends = await self.user.aget_friends()
        logger.debug(f'Consumer, friends: {friends}')
        logger.debug(f'self.user.id = ${self.user.id}')
        for friend in friends:
            logger.debug(f'Boucle for, friend: {friend}')
            await self.send_user_info(self.user.id, friend)

    async def disconnect(self, close_code):
        from django_otp import devices_for_user
        from asgiref.sync import sync_to_async

        try:
            # Only try to get user if we have a user_id
            if hasattr(self, 'user_id'):
                self.user = await self.get_user()
                
                if self.user and self.user.is_authenticated:
                    await self.update_user_status(False)
                    await self.send_status_friends(False)

                    @sync_to_async
                    def delete_unconfirmed_2fa_auth(user):
                        for device in devices_for_user(user, confirmed=False):
                            device.delete()
                        return True
                        
                    await delete_unconfirmed_2fa_auth(self.user)
                    
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

    async def send_user_info(self, receiver_id, user_info):
        channel_layer = get_channel_layer()
        await channel_layer.group_send(
            f"user_{receiver_id}",
            {
                'type': "friend_list_user_update",
                "user": {
                    "id": user_info['id'],  # Utilise l'accès dictionnaire
                    "username": user_info['username'],  # Utilise l'accès dictionnaire
                    "is_online": user_info['is_online'],  # Ajoute le vrai statut
                    "avatar": user_info['avatar']
                }
            }
        )

    @database_sync_to_async
    def update_user_status(self, is_online):
        self.user.update_user_status(is_online)
        
    @database_sync_to_async
    def get_user(self):
        try:
            return CustomUser.objects.get(id=self.user_id)
        except CustomUser.DoesNotExist:
            logger.error(f"User with id {self.user_id} not found")
            return None

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