from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from authenticationApp.models import Notification

import logging
logger = logging.getLogger(__name__)

async def send_notification(receiver_id, notification):
    channel_layer = get_channel_layer()
    await channel_layer.group_send(
        f"user_{receiver_id}",
        notification.to_group_send_format()
    )

class FriendRequestService:
    @staticmethod
    async def create_and_send_friend_request(sender, receiver):
        friendship = await sender.create_friendship(receiver)

        if friendship:
            notification = await Notification.objects.acreate(
                recipient=receiver,
                sender=sender,
                content=f"{sender.username} sent you a friend request",
                notification_type="friend_request_received"
            )
            await send_notification(receiver.id, notification)
            return True
        # Friendship already exists
        return False

    @staticmethod
    async def accept_friend_request(user, notification_id):
        logger.debug("accept_friend_request debut")

        @database_sync_to_async
        def get_notification_and_sender(notification_id):
            notification = Notification.objects.filter(id=notification_id).select_related('sender').first()
            if notification:
                return notification.sender
            return None

        from_user = await get_notification_and_sender(notification_id)
        logger.debug(f"from_user={from_user}")
        if from_user:
            result = await user.accept_friend_request(from_user)
            logger.debug("accept_friend_request fin")
            return result

        logger.debug("accept_friend_request fin sans notification")
