from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from chat.models import Room, Message


class RoomListView(ListView):
    model = Room
    context_object_name = 'room_list'

class RoomDetailView(DetailView):
    model = Room

    def get_context_data(self, **kwargs):
        room = self.get_object()
        message_list = Message.objects.filter(room=room)[:25]

        context = super().get_context_data(**kwargs)
        context['message_list'] = message_list
        context['room'] = room

        return context
