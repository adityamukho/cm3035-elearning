from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import *

router = DefaultRouter()
router.register(r'courses', CourseViewSet)
router.register(r'course-materials', CourseMaterialViewSet)
router.register(r'lectures', LectureViewSet)
router.register(r'assignments', AssignmentViewSet)
router.register(r'assignment-questions', AssignmentQuestionViewSet)
router.register(r'mcq-options', MCQOptionViewSet)
router.register(r'assignment-submissions', AssignmentSubmissionViewSet)
router.register(r'question-responses', QuestionResponseViewSet)
router.register(r'feedbacks', FeedbackViewSet)


urlpatterns = [
    path('heartbeat/', heartbeat, name="heartbeat"),
    path("", home, name="home"),
    path('courses/', CourseListView.as_view(), name='courses'),
    path('course/<int:pk>/', CourseDetailView.as_view(), name='course-view'),
    path('course/create/', CourseCreateView.as_view(), name='course-create'),
    path('course/<int:pk>/update/', CourseUpdateView.as_view(), name='course-update'),
    path('course/<int:pk>/delete/', CourseDeleteView.as_view(), name='course-delete'),
    path('course/<int:pk>/leave/', CourseLeaveView.as_view(), name='course-leave'),
    path('course/<int:course_id>/material/', CourseMaterialListView.as_view(), name='course-material'),
    path('course/material/<int:pk>/', CourseMaterialDetailView.as_view(), name='course-material-view'),
    path('course/<int:course_id>/add-material/', AddCourseMaterialView.as_view(), name='add-course-material'),
    path('course/<int:course_id>/remove-student/<int:student_id>/', RemoveStudentView.as_view(), name='remove-student'),
    path('course/<int:course_id>/block-student/<int:student_id>/', BlockStudentView.as_view(), name='block-student'),
    path('course/<int:course_id>/add-students/', AddStudentsView.as_view(), name='add-students'),
    path('student-search/', StudentSearchView.as_view(), name='student-search'),
    path('course/<int:course_id>/enroll/', CourseEnrollView.as_view(), name='course_enroll'),
    path('courses/<int:course_id>/unblock-student/<int:student_id>/', UnblockStudentView.as_view(), name='unblock-student'),
    path('search/', SearchView.as_view(), name='search'),
    path('course/<int:course_id>/feedback/', CourseFeedbackView.as_view(), name='course-feedback'),
    path('assignment/<int:assignment_id>/submit/', SubmitAssignmentView.as_view(), name='submit-assignment'),
    path('course/material/<int:pk>/edit/', EditCourseMaterialView.as_view(), name='edit-course-material'),
    path('assignment/<int:assignment_id>/add-question/', AddAssignmentQuestionView.as_view(), name='add-assignment-question'),
    path('course-material/<int:pk>/delete/', DeleteCourseMaterialView.as_view(), name='delete-course-material'),
    path('assignment-question/<int:pk>/delete/', DeleteAssignmentQuestionView.as_view(), name='delete-assignment-question'),
    path('course/<int:course_id>/submissions/', CourseSubmissionsView.as_view(), name='course-submissions'),
    path('submission/<int:pk>/', ViewSubmissionView.as_view(), name='view-submission'),
    path('submission/<int:pk>/grade/', GradeSubmissionView.as_view(), name='grade-submission'),
    path('course/<int:course_id>/my-submissions/', MySubmissionsView.as_view(), name='my-submissions'),
    path('course/<int:course_id>/student/<int:student_id>/submissions/', StudentSubmissionsView.as_view(), name='student-submissions'),
    path('api/', include(router.urls)),
]
