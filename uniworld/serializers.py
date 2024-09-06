from rest_framework import serializers
from .models import Course, CourseMaterial, Lecture, Assignment, AssignmentSubmission, AssignmentQuestion, QuestionResponse, MCQOption, Feedback

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'name', 'description', 'teacher', 'students', 'blocked_students', 'chat_room']

class CourseMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseMaterial
        fields = ['id', 'course', 'title', 'type', 'sequence']

class LectureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lecture
        fields = ['id', 'material', 'content', 'document', 'video_url']

class AssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = ['id', 'material', 'due_date']

class AssignmentQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignmentQuestion
        fields = ['id', 'assignment', 'question_text', 'question_type']

class MCQOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MCQOption
        fields = ['id', 'question', 'option_text', 'is_correct']

class AssignmentSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignmentSubmission
        fields = ['id', 'assignment', 'student', 'submission_date', 'grade']

class QuestionResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionResponse
        fields = ['id', 'submission', 'question', 'response_text', 'selected_option']

class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ['id', 'course', 'user', 'rating', 'comment', 'created_at']