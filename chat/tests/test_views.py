import pytest
from django.urls import reverse

from chat.models import Room


@pytest.mark.django_db
def test_room_list_view(client):
    Room.objects.create(name="Test Room", slug="test-room")
    url = reverse('rooms')
    response = client.get(url)
    assert response.status_code == 200
    assert 'room_list' in response.context

@pytest.mark.django_db
def test_room_detail_view(client):
    room = Room.objects.create(name="Test Room", slug="test-room")
    url = reverse('room', args=[room.pk])
    response = client.get(url)
    assert response.status_code == 200
    assert 'room' in response.context
    assert 'message_list' in response.context
