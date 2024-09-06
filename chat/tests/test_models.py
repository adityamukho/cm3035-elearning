from django.test import TestCase
from django.contrib.auth import get_user_model
from chat.models import Room, Message

User = get_user_model()

class RoomModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.room = Room.objects.create(name='Test Room', slug='test-room', creator=self.user)

    def test_room_creation(self):
        self.assertEqual(self.room.name, 'Test Room')
        self.assertEqual(self.room.slug, 'test-room')
        self.assertEqual(self.room.creator, self.user)

    def test_room_str_representation(self):
        self.assertEqual(str(self.room), 'Test Room')

class MessageModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.room = Room.objects.create(name='Test Room', slug='test-room', creator=self.user)
        self.message = Message.objects.create(room=self.room, user=self.user, content='Test message')

    def test_message_creation(self):
        self.assertEqual(self.message.room, self.room)
        self.assertEqual(self.message.user, self.user)
        self.assertEqual(self.message.content, 'Test message')
        self.assertFalse(self.message.flagged)
        self.assertEqual(self.message.flagged_categories, '')

    def test_message_ordering(self):
        self.assertEqual(Message._meta.ordering, ('date_added',))