from django.urls import path

from .views import *

urlpatterns = [
    path('heartbeat/', heartbeat, name="heartbeat"),
    path("", home, name="home"),
    path('courses/', CourseListView.as_view(), name='courses'),
    path('course/<int:pk>/', CourseDetailView.as_view(), name='course-detail'),
    path('course/create/', CourseCreateView.as_view(), name='course-create'),
    path('course/<int:pk>/update/', CourseUpdateView.as_view(), name='course-update'),
    path('course/<int:pk>/delete/', CourseDeleteView.as_view(), name='course-delete'),
    path('course/<int:pk>/leave/', CourseLeaveView.as_view(), name='course-leave'),
    path('course/<int:course_id>/remove-student/<int:student_id>/', RemoveStudentView.as_view(), name='remove-student'),
    path('course/<int:course_id>/block-student/<int:student_id>/', BlockStudentView.as_view(), name='block-student'),
    path('course/<int:course_id>/add-students/', AddStudentsView.as_view(), name='add-students'),
    path('student-search/', StudentSearchView.as_view(), name='student-search'),
    path('course/<int:course_id>/enroll/', CourseEnrollView.as_view(), name='course_enroll'),
]
