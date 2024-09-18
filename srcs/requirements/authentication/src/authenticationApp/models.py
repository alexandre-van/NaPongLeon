from django.contrib.auth.models import AbstractUser
from django.db import models
#from django.contrib.staticfiles.storage import staticfiles_storage
from django.templatetags.static import static
import os

def user_avatar_path(instance, filename):
    return f'users/{instance.id}/avatar/{filename}'

def default_avatar_path():
    return ''

class CustomUser(AbstractUser):
    avatar = models.ImageField(upload_to=user_avatar_path, null=True, blank=True)
    nickname = models.CharField(max_length=30, unique=True, null=True, blank=True)

    @property
    def avatar_url(self):
        if self.avatar and hasattr(self.avatar, 'url'):
            return self.avatar.url
        else:
            return static('images/default_avatar.png')
#            return staticfiles_storage.url('images/default_avatar.png')

#    def save(self, *args, **kwargs):
#        if self.pk: # if primary key, exists in db
#            try:
#                old_avatar = CustomUser.objects.get(pk=self.pk).avatar
#                if old_avatar and self.avatar and old_avatar != self.avatar:
#                    if os.path.isfile(old_avatar.path):
#                        os.remove(old_avatar.path)
#            except CustomUser.DoesNotExist:
#                pass
#        super().save(*args, **kwargs)

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

    def delete(self, *args, **kwargs):
        if self.avatar:
            avatar_path = os.path.join(settings.MEDIA_ROOT, self.avatar.name)
            if os.path.isfile(avatar_path):
                os.remove(avatar_path)
                print(f"Deleted avatar during user deletion: {avatar_path}")
        super().delete(*args, **kwargs)
