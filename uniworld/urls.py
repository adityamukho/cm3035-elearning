from django.urls import path

from .views import *

urlpatterns = [
    path('heartbeat/', heartbeat, name="heartbeat"),
    path("", home, name="home"),
    path('courses/', CourseListView.as_view(), name='courses'),
    path('course/<int:pk>/', CourseDetailView.as_view(), name='course'),
    path('course/create/', CourseCreateView.as_view(), name='course-create'),
    path('course/<int:pk>/update/', CourseUpdateView.as_view(), name='course-update'),
    path('course/<int:pk>/delete/', CourseDeleteView.as_view(), name='course-delete'),
    path('course/<int:pk>/leave/', CourseLeaveView.as_view(), name='course-leave'),
    path('course/<int:course_id>/remove-student/<int:student_id>/', remove_student, name='remove-student'),
]
