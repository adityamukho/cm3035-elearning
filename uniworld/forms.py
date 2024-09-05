from django import forms
from .models import CourseMaterial, Lecture, Assignment

class CourseMaterialForm(forms.ModelForm):
    class Meta:
        model = CourseMaterial
        fields = ['title', 'type', 'sequence']

class LectureForm(forms.ModelForm):
    class Meta:
        model = Lecture
        fields = ['content', 'video_url', 'document']

class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['due_date', 'questions']
