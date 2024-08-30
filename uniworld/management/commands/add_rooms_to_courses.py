from django.core.management.base import BaseCommand
from uniworld.models import Course
from chat.models import Room

class Command(BaseCommand):
    help = 'Adds chat rooms to existing courses that do not have one'

    def handle(self, *args, **options):
        courses_without_rooms = Course.objects.filter(chat_room__isnull=True)
        rooms_created = 0

        for course in courses_without_rooms:
            room = Room.objects.create(name=f"Chat for {course.name}")
            course.chat_room = room
            course.save()
            rooms_created += 1

        self.stdout.write(self.style.SUCCESS(f'Successfully created {rooms_created} chat rooms'))
