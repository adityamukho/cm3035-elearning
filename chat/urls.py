from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import *

router = DefaultRouter()
router.register(r'rooms', RoomViewSet)
router.register(r'messages', MessageViewSet)

urlpatterns = [
    path('rooms/', RoomListView.as_view(), name='rooms'),
    path('room/<int:pk>/', RoomDetailView.as_view(), name='room'),
    # path('room/create/', roomCreateView.as_view(), name='room-create'),
    # path('room/<int:pk>/update/', roomUpdateView.as_view(), name='room-update'),
    # path('room/<int:pk>/delete/', roomDeleteView.as_view(), name='room-delete'),
    path('api/', include(router.urls)),
]
