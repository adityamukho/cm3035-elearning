from django.db.models.signals import pre_save
from django.dispatch import receiver
from openai import OpenAI, APIError

from .models import Message
from .tasks import send_api_error_mail

client = OpenAI()

# noinspection PyUnusedLocal
@receiver(pre_save, sender=Message)
def create_message(sender, instance, **kwargs):
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
