from rest_framework import serializers
from .models import Room, Message

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['id', 'name', 'slug', 'creator']

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'room', 'user', 'content', 'flagged', 'flagged_categories', 'date_added']
