from django.db import models
from django.contrib.auth.models import User

class Room(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField()
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_rooms')

class Message(models.Model):
    class Meta:
        ordering = ('date_added',)

    room = models.ForeignKey(Room, related_name='messages', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='messages', on_delete=models.CASCADE)
    content = models.TextField()
    flagged = models.BooleanField(default=False)
    flagged_categories = models.TextField(blank=True)
    date_added = models.DateTimeField(auto_now_add=True)
