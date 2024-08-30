import json

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer


# Create a consumer class
class ChatConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)

        self.room_group_name = None
        self.room_name = None
        self.moderator = None

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        message = data['message']
        username = data['username']
        room = data['room']

        msg = await self.save_message(username, room, message)
        if msg.flagged:
            moderator = await self.get_moderator()

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': f'''
                        Warning @{username}: Your message violates our content policy
                        and has been redacted! It has been flagged as "{msg.flagged_categories}".
                        Repeated violations will incur strict disciplinary action.
                    ''',
                    'username': moderator.username
                }
            )
        else:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'username': username
                }
            )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        username = event['username']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'username': username
        }))

    @sync_to_async
    def save_message(self, username, room, message):
        from .models import Room, Message
        from django.contrib.auth.models import User

        user = User.objects.get(username=username)
        room = Room.objects.get(slug=room)

        return Message.objects.create(user=user, room=room, content=message)

    @sync_to_async
    def get_moderator(self):
        if self.moderator is None:
            from django.contrib.auth.models import User

            self.moderator = User.objects.get(username="moderator")

        return self.moderator
