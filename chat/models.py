from django.db import models
from django.conf import settings

# Replace direct User import with this:
User = settings.AUTH_USER_MODEL

from django.utils.text import slugify
from django.db.models.signals import pre_save
from django.dispatch import receiver

class Room(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_rooms')

    def __str__(self):
        return self.name

@receiver(pre_save, sender=Room)
def create_room_slug(sender, instance, *args, **kwargs):
    if not instance.slug:
        base_slug = slugify(instance.name)
        slug = base_slug
        n = 1
        while Room.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{n}"
            n += 1
        instance.slug = slug

class Message(models.Model):
    class Meta:
        ordering = ('date_added',)

    room = models.ForeignKey(Room, related_name='messages', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='messages', on_delete=models.CASCADE)
    content = models.TextField()
    flagged = models.BooleanField(default=False)
    flagged_categories = models.TextField(blank=True)
    date_added = models.DateTimeField(auto_now_add=True)
