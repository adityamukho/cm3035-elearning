from django.db.models.signals import pre_save
from django.dispatch import receiver
from openai import OpenAI, APIError
from django.utils.text import slugify

from .models import Message, Room
from .tasks import send_api_error_mail

import os

client = OpenAI() if os.environ.get('OPENAI_API_KEY') else None

# noinspection PyUnusedLocal
@receiver(pre_save, sender=Message)
def create_message(sender, instance, **kwargs):
    if client:
        try:
            response = client.moderations.create(
                input=instance.content,
            )
            if len(response.results):
                result = response.results[0]
                if result.flagged:
                    instance.flagged = True

                    attrs = dir(result.categories)
                    flags = []
                    for attr in attrs:
                        value = getattr(result.categories, attr)
                        if isinstance(value, bool) and value:
                            flags.append(attr)
                    instance.flagged_categories = ', '.join(flags)
        except APIError as e:
            send_api_error_mail.delay(e.message)

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