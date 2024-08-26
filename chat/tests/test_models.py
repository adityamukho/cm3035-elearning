import pytest
from django.contrib.auth.models import User

from chat.models import Room, Message


@pytest.mark.django_db
def test_room_creation():
    room = Room.objects.create(name="Test Room", slug="test-room")
    assert room.name == "Test Room"
    assert room.slug == "test-room"

@pytest.mark.django_db
def test_message_creation():
    user = User.objects.create_user(username='testuser', password='12345')
    room = Room.objects.create(name="Test Room", slug="test-room")
    message = Message.objects.create(user=user, room=room, content="Hello World")
    assert message.content == "Hello World"
    assert message.user == user
    assert message.room == room
