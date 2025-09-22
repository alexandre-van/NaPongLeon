from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
from authenticationApp.models import Notification

async def send_notification(receiver_id, notification):
    channel_layer = get_channel_layer()
    await channel_layer.group_send(
        f"user_{receiver_id}",
        notification.to_group_send_format()
    )

async def send_user_info(receiver_id, user_info):
    channel_layer = get_channel_layer()
    await channel_layer.group_send(
        f"user_{receiver_id}",
        {
            'type': "friend_list_user_update",
            "user": {
                "id": user_info.id,
                "username": user_info.username,
                "is_online": True,
            }
        }
    )

async def send_deleted_friend_from_list(user, friend_id):
    channel_layer = get_channel_layer()
    await channel_layer.group_send(
        f"user_{friend_id}",
        {
            'type': "friend_deleted",
            'friend_id': user.id
        }
    )

@database_sync_to_async
def get_notification_and_sender(notification_id):
    notification = Notification.objects.filter(id=notification_id).select_related('sender').first()
    if notification:
        return notification, notification.sender
    return None


class FriendRequestService:
    @staticmethod
    async def create_and_send_friend_request(sender, receiver):
        notification = await sender.create_friendship(receiver)

        if notification:
            await send_notification(receiver.id, notification)
            return True
        # Friendship already exists
        return False

    @staticmethod
    async def accept_friend_request(user, notification_id):
        notification, from_user = await get_notification_and_sender(notification_id)
        if from_user:
            await send_user_info(from_user.id, user) # To friend
            await send_user_info(user.id, from_user) # To sender
            notification = await user.accept_friend_request(from_user, notification)
            if notification:
                await send_notification(from_user.id, notification)
                return True
        return False

    @staticmethod
    async def reject_friend_request(user, notification_id):
        notification, from_user = await get_notification_and_sender(notification_id)
        if from_user:
            await user.reject_friend_request(from_user, notification)
            if notification:
                return True
        return False

    @staticmethod
    async def delete_self_from_ex_friend_list(user, friend_id):
        await send_deleted_friend_from_list(user, friend_id)