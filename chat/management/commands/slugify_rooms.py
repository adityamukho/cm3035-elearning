from django.core.management.base import BaseCommand
from django.utils.text import slugify
from chat.models import Room

class Command(BaseCommand):
    help = 'Generates slugs for rooms that do not have one'

    def handle(self, *args, **options):
        rooms_updated = 0
        rooms = Room.objects.filter(slug__isnull=True) | Room.objects.filter(slug='')

        for room in rooms:
            base_slug = slugify(room.name)
            slug = base_slug
            n = 1
            while Room.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{n}"
                n += 1
            room.slug = slug
            room.save()
            rooms_updated += 1

        self.stdout.write(self.style.SUCCESS(f'Successfully updated {rooms_updated} rooms'))
