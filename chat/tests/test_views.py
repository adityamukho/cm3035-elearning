from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from chat.models import Room, Message

User = get_user_model()

class RoomListViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.room = Room.objects.create(name='Test Room', slug='test-room', creator=self.user)

    def test_view_url_exists_at_desired_location(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get('/chat/rooms/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('rooms'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('rooms'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'chat/room_list.html')

class RoomDetailViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.room = Room.objects.create(name='Test Room', slug='test-room', creator=self.user)
        self.message = Message.objects.create(room=self.room, user=self.user, content='Test message')

    def test_view_url_exists_at_desired_location(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(f'/chat/room/{self.room.pk}/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('room', args=[self.room.pk]))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('room', args=[self.room.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'chat/room_detail.html')

    def test_context_data(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('room', args=[self.room.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertIn('message_list', response.context)
        self.assertIn('room', response.context)
        self.assertIn('users', response.context)