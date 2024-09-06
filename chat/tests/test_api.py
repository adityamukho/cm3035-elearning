from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from chat.models import Room, Message
from chat.serializers import RoomSerializer, MessageSerializer
from uniworld.models import Course

User = get_user_model()

class RoomAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.force_authenticate(user=self.user)
        self.room = Room.objects.create(name='Test Room', slug='test-room', creator=self.user)

    def test_get_rooms(self):
        url = reverse('room-list')
        response = self.client.get(url)
        rooms = Room.objects.all()
        serializer = RoomSerializer(rooms, many=True)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_room(self):
        url = reverse('room-list')
        data = {'name': 'New Room', 'slug': 'new-room', 'creator': self.user.id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_room_creation_on_course_creation(self):
        initial_room_count = Room.objects.count()
        course = Course.objects.create(name='Test Course', teacher=self.user)
        self.assertEqual(Room.objects.count(), initial_room_count + 1)
        self.assertIsNotNone(course.chat_room)
        self.assertEqual(course.chat_room.name, f"Chat for {course.name}")

class MessageAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.force_authenticate(user=self.user)
        self.room = Room.objects.create(name='Test Room', slug='test-room', creator=self.user)
        self.message = Message.objects.create(room=self.room, user=self.user, content='Test message')

    def test_get_messages(self):
        url = reverse('message-list')
        response = self.client.get(url)
        messages = Message.objects.all()
        serializer = MessageSerializer(messages, many=True)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_message(self):
        url = reverse('message-list')
        data = {'room': self.room.id, 'user': self.user.id, 'content': 'New message'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)