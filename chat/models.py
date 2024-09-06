from django.db import models
from django.conf import settings
from rules import is_group_member, always_deny, is_authenticated
from rules.contrib.models import RulesModel

User = settings.AUTH_USER_MODEL

class Room(RulesModel):
    class Meta:
        rules_permissions = {
            'view': is_authenticated,
            'add': is_group_member('teachers'),
            'change': always_deny,
            'delete': always_deny,
        }

    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_rooms')

    def __str__(self):
        return self.name

class Message(RulesModel):
    class Meta:
        ordering = ('date_added',)
        rules_permissions = {
            'view': is_authenticated,
            'add': is_authenticated,
            'change': always_deny,
            'delete': always_deny,
        }

    room = models.ForeignKey(Room, related_name='messages', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='messages', on_delete=models.CASCADE)
    content = models.TextField()
    flagged = models.BooleanField(default=False)
    flagged_categories = models.TextField(blank=True)
    date_added = models.DateTimeField(auto_now_add=True)
