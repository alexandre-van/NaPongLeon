from channels.db import database_sync_to_async
from django.contrib.auth.models import AbstractUser
from django.db.models import UniqueConstraint, Q
from django.db import models
from asgiref.sync import sync_to_async
#from django.contrib.staticfiles.storage import staticfiles_storage
from django.templatetags.static import static
import os

import logging
logger = logging.getLogger(__name__)


def user_avatar_path(instance, filename):
    return f'users/{instance.id}/avatar/{filename}'

class FriendshipStatus(models.TextChoices):
    PENDING = 'PE', 'Pending'
    ACCEPTED = 'AC', 'Accepted'

class CustomUser(AbstractUser):
    avatar = models.ImageField(upload_to=user_avatar_path, null=True, blank=True)
    nickname = models.CharField(max_length=30, unique=True, null=True, blank=True)
    friends = models.ManyToManyField(
        'self',
        through='Friendship',
        symmetrical=False,
        related_name="friended_by"
    )
    is_online = models.BooleanField(default=False)

    @property
    def avatar_url(self):
        if self.avatar and hasattr(self.avatar, 'url'):
            return self.avatar.url
        else:
            return static('images/default_avatar.png')

    def save(self, *args, **kwargs):
        if self.pk:
            try:
                old_instance = CustomUser.objects.get(pk=self.pk)
                if old_instance.avatar and self.avatar != old_instance.avatar and old_instance.avatar.name:
                    old_avatar_path = os.path.join(settings.MEDIA_ROOT, old_instance.avatar.name)
                    if os.path.isfile(old_avatar_path):
                        os.remove(old_avatar_path)
                        print(f"Deleted old avatar: {old_avatar_path}")
            except CustomUser.DoesNotExist:
                pass
        super().save(*args, **kwargs)

    async def asave(self, *args, **kwargs):
        await sync_to_async(super().save)(*args, **kwargs)

    async def update_user_status(self, is_online):
        self.is_online = is_online
        await self.asave()

    async def update_nickname(self, nickname):
        self.nickname = nickname
        await self.asave()
    
    async def update_avatar_url(self, avatar_url):
        self.avatar = avatar_url
        await self.asave()

    def delete(self, *args, **kwargs):
        if self.avatar:
            avatar_path = os.path.join(settings.MEDIA_ROOT, self.avatar.name)
            if os.path.isfile(avatar_path):
                os.remove(avatar_path)
                print(f"Deleted avatar during user deletion: {avatar_path}")
        super().delete(*args, **kwargs)

    async def create_friendship(self, to_user):
        logger.debug(f"self={self} ------- to_user={to_user}\n\n")
        if (to_user != self):
            try:
                friendship, created = await Friendship.aget_or_create_friendship(self, to_user)

                if created:
                    notification = await Notification.objects.acreate(
                        sender=self,
                        recipient=to_user,
                        notification_type="friend_request"
                    )
                    return notification
                return false
            except Exception as e:
                logger.error(f"Error creating friendship: {e}")
                return None
        return None

    @database_sync_to_async
    def accept_friend_request(self, from_user, notification):
        logger.debug("CustomUser: accept_friend_request debut")
        if (from_user != self):
            friendship = Friendship.objects.filter(
                from_user=from_user,
                to_user=self,
                status=FriendshipStatus.PENDING
            ).first()
            logger.debug(f"CustomUser: accept_friend_request avant friendship: friendship={friendship}\nfriendship.from_user={friendship.from_user}\nfriendship.to_user={friendship.to_user}\n")
            if friendship:
                logger.debug(f"dans le if de friendship friendship.status={friendship.status}\n")
                friendship.status = FriendshipStatus.ACCEPTED
                friendship.save()
            if notification:
                notification.sender = self
                notification.recipient = from_user
                notification.notification_type = 'friend_request_accepted'
                notification.save()
                return notification
            return None
        return None

    @database_sync_to_async
    def reject_friend_request(self, from_user, notification):
        if (from_user != self):
            Friendship.objects.filter(
                from_user=from_user,
                to_user=self,
                status=FriendshipStatus.PENDING
            ).delete()
            if notification:
                notification.delete()
            return True
        return False

    @database_sync_to_async
    def remove_friend_from_list(self, friend):
        # Request to show friendships where user is 'from_user'
        friends_as_from = self.friendships_sent.filter(to_user=friend, status=FriendshipStatus.ACCEPTED).first()
        if friends_as_from:
            friends_as_from.delete()
            return True
            
        # Request to show friendships where user is 'to_user'
        friends_as_to = self.friendships_received.filter(from_user=friend, status=FriendshipStatus.ACCEPTED).first()
        if friends_as_to:
            friends_as_to.delete()
            return True
        return False


    async def aget_friends(self):
        @sync_to_async
        def get_friends():
            # Request to show friendships where user is 'from_user'
            friends_as_from = self.friendships_sent.filter(status=FriendshipStatus.ACCEPTED).values_list('to_user', flat=True)
            
            # Request to show friendships where user is 'to_user'
            friends_as_to = self.friendships_received.filter(status=FriendshipStatus.ACCEPTED).values_list('from_user', flat=True)

            # Combine both sets of friendships
            friend_ids = list(set(friends_as_from) | set(friends_as_to))

            # Formate data in correct way
            friends = list(CustomUser.objects.filter(id__in=friend_ids).values(
                'id',
                'username',
                'nickname',
                'is_online',
                'avatar'
            ))
            return friends

        return await get_friends()

    def get_friends(self):
        return CustomUser.objects.filter(
            models.Q(friendships_sent__from_user=self, friendships_sent__status=FriendshipStatus.ACCEPTED) |
            models.Q(friendships_received__to_user=self, friendships_received__status=FriendshipStatus.ACCEPTED)
        ).distinct()

    def get_pending_friend_requests(self):
        return CustomUser.objects.filter(
            friendships_sent__to_user=self,
            friendships_sent__status=FriendshipStatus.PENDING
        )



class Friendship(models.Model):
    from_user = models.ForeignKey(CustomUser, related_name='friendships_sent', on_delete=models.CASCADE)
    to_user = models.ForeignKey(CustomUser, related_name='friendships_received', on_delete=models.CASCADE)
    status = models.CharField(max_length=2, choices=FriendshipStatus.choices, default=FriendshipStatus.PENDING, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['from_user', 'to_user'],
                name='unique_friendship'
            )
        ]
        indexes = [
            models.Index(fields=['status', 'from_user']),
            models.Index(fields=['status', 'to_user']),
        ]

    @classmethod
    async def aget_or_create_friendship(cls, from_user, to_user):
        try:
            friendship = await cls.objects.aget(
                Q(from_user=from_user, to_user=to_user) |
                Q(from_user=to_user, to_user=from_user)
            )
            return friendship, False
        except cls.DoesNotExist:
            friendship = await cls.objects.acreate(
                from_user=from_user,
                to_user=to_user,
                status=FriendshipStatus.PENDING
            )
            return friendship, True



class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('friend_request', 'Friend request'),
        ('friend_request_accepted', 'Friend request accepted'),
        ('friend_request_rejected', 'Friend request rejected'),
    ]

    sender = models.ForeignKey(CustomUser, related_name='sender_notification', on_delete=models.CASCADE)
    recipient = models.ForeignKey(CustomUser, related_name='notifications', on_delete=models.CASCADE, null=True, blank=True)
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            UniqueConstraint(
                fields=['recipient', 'sender', 'notification_type'],
                condition=Q(notification_type='friend_request'),
                name='unique_friend_request'
            )
        ]

    def to_dict(self):
        logger.debug(f"to_dict notification")
        return {
            "id": self.recipient.id,
            "recipient_username": self.recipient.username,
            "sender_username": self.sender.username,
            "notification_type": self.notification_type,
            "created_at": self.created_at.isoformat(),
            "is_read": self.is_read,
            "type": 'notification'
        }

    def to_group_send_format(self):
        logger.debug(f"to_group_send_format notification username: {self.recipient.username}")
        return {
                "type": "notification", # Gets the notification method in Consumers called
                "notification": self.to_dict()
        }

    async def mark_as_read(self):
        self.is_read = True
        self.asave()

    @classmethod
    async def get_unread_notifications(cls, user):
        return await cls.objects.filter(recipient=user, is_read=False)

    @classmethod
    async def get_all_notifications(cls, user):
        @sync_to_async
        def get_notifications():
            return list(cls.objects.filter(Q(recipient=user) | Q(sender=user)).select_related(
                    'recipient', 'sender'
                ).order_by('-created_at').values(
                    'id',
                    'recipient__username',
                    'sender__username',
                    'notification_type',
                    'created_at',
                ))

        return await get_notifications()

    @classmethod
    async def get_all_received_notifications(cls, user):
        @sync_to_async
        def get_received_notifications():
            return list(cls.objects.filter(Q(recipient=user)).order_by('-created_at').values(
                'id',
                'recipient__username',
                'sender__username',
                'notification_type',
                'created_at'
            ))
        return await get_received_notifications()

    @classmethod
    @database_sync_to_async
    def delete_notification(cls, notification_id):
        notification = cls.objects.get(id=notification_id)
        if notification:
            notification.delete()
            return True
        return False
