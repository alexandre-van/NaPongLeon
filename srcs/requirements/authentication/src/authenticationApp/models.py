from django.db import models

from django.contrib.auth.models import AbstractUser
from django.db import models

def user_avatar_path(instance, filename):
    return f'users/{instance.id}/avatar/{filename}'

class CustomUser(AbstractUser):
    avatar = models.ImageField(upload_to=user_avatar_path, null=True, blank=True)

    @property
    def avatar_url(self):
        if self.avatar and hasattr(self.avatar, 'url'):
            return self.avatar.url
        else:
            return f"{settings.STATIC_URL}images/default_avatar.png"

    def save(self, *args, **kwargs):
        if self.pk: # if primary key, exists in db
            try:
                old_avatar = CustomUser.objects.get(pk=self.pk).avatar
                if old_avatar and self.avatar and old_avatar != self.avatar:
                    if os.path.isfile(old_avatar.path):
                        os.remove(old_avatar.path)
            except CustomUser.DoesNotExist:
                pass
        super().save(*args, **kwargs)

