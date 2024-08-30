from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.contrib.auth.models import User

from chat.models import Room, Message


class RoomListView(ListView):
    model = Room
    context_object_name = 'room_list'

class RoomDetailView(DetailView):
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
