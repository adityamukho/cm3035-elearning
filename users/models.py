from django.db import models
from django.contrib.auth.models import User
from PIL import Image
from rules.contrib.models import RulesModel
from rules import Predicate, always_deny, is_authenticated

is_profile_owner = Predicate(lambda user, profile: profile.user == user)

class Profile(RulesModel):
    class Meta:
        rules_permissions = {
            'view': is_authenticated,
            'add': always_deny,
            'change': is_profile_owner,
            'delete': always_deny,
        }

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    avatar = models.ImageField(
        default='avatar.jpg',  # default avatar
        upload_to='profile_avatars'  # dir to store the image
    )

    def __str__(self):
        # noinspection PyUnresolvedReferences
        return f'{self.user.username} Profile'

    def save(self, *args, **kwargs):
        # save the profile first
        super().save(*args, **kwargs)

        # resize the image
        img = Image.open(self.avatar.path)
        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            # create a thumbnail
            img.thumbnail(output_size)
            # overwrite the larger image
            img.save(self.avatar.path)
