from django.urls import path

from .views import *

urlpatterns = [
    path("heartbeat", heartbeat, name="heartbeat"),
    path("", home, name="home"),
    path('courses/', CourseListView.as_view(), name='courses'),
]