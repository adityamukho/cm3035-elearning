from django.core.management.base import BaseCommand
from chat.models import Message

class Command(BaseCommand):
    help = 'Truncates the Message table'

    def handle(self, *args, **options):
        message_count = Message.objects.count()
        Message.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f'Successfully deleted {message_count} messages'))
