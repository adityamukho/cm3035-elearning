from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin

from chat.models import Room, Message
from rest_framework import viewsets
from .serializers import RoomSerializer, MessageSerializer
from rules.contrib.rest_framework import AutoPermissionViewSetMixin
from rules.contrib.views import AutoPermissionRequiredMixin

User = get_user_model()

class RoomListView(LoginRequiredMixin, ListView):
    model = Room
    context_object_name = 'room_list'

class RoomDetailView(AutoPermissionRequiredMixin, DetailView):
    model = Room
    template_name = 'chat/room_detail.html'

    def get_context_data(self, **kwargs):
        room = self.get_object()
        message_list = Message.objects.filter(room=room, flagged__in=[False, None]).order_by('-date_added')[:25][::-1]
        users = User.objects.values('id', 'username')

        context = super().get_context_data(**kwargs)
        context['message_list'] = message_list
        context['room'] = room
        context['users'] = users
        return context

class RoomViewSet(AutoPermissionViewSetMixin, viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer

class MessageViewSet(AutoPermissionViewSetMixin, viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
