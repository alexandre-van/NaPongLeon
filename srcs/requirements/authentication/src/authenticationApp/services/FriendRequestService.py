from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from authenticationApp.models import Notification

async def send_notification(receiver_id, notification):
    channel_layer = get_channel_layer()
    await channel_layer.group_send(
        f"user_{receiver_id}",
        notification.to_group_send_format()
    )

class FriendRequestService:
    @staticmethod
    async def create_and_send_friend_request(sender, receiver):
        friendship = await sender.send_friend_request(receiver)

        if friendship:
            notification = await Notification.objects.acreate(
                user=receiver,
                content=f"{sender.username} sent you a friend request",
                notification_type="friend_request_received"
            )
            await send_notification(receiver.id, notification)
            return True
        # Friendship already exists
        return False
        
