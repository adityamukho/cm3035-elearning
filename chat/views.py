from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from chat.models import Room


class RoomListView(ListView):
    model = Room
    context_object_name = 'room_list'

class RoomDetailView(DetailView):
    model = Room
    context_object_name = 'room'
