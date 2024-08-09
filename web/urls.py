from django.urls import path

from .views import home, CourseListView

urlpatterns = [
    path("", home, name="home"),
    path('courses/', CourseListView.as_view(), name='courses'),
]