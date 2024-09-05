from django import forms
from .models import CourseMaterial, Lecture, Assignment, AssignmentQuestion, MCQOption, AssignmentSubmission, QuestionResponse

class CourseMaterialForm(forms.ModelForm):
    class Meta:
        model = CourseMaterial
        fields = ['title', 'type', 'sequence']

class LectureForm(forms.ModelForm):
    class Meta:
        model = Lecture
        fields = ['content', 'video_url', 'document']

class AssignmentForm(forms.ModelForm):
    due_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    
    class Meta:
        model = Assignment
        fields = ['due_date']

class AssignmentQuestionForm(forms.ModelForm):
    class Meta:
        model = AssignmentQuestion
        fields = ['question_text', 'question_type', 'marks']

class MCQOptionForm(forms.ModelForm):
    class Meta:
        model = MCQOption
        fields = ['option_text', 'is_correct']

MCQOptionFormSet = forms.inlineformset_factory(AssignmentQuestion, MCQOption, form=MCQOptionForm, extra=4, can_delete=True)

class AssignmentSubmissionForm(forms.ModelForm):
    class Meta:
        model = AssignmentSubmission
        fields = []

class QuestionResponseForm(forms.ModelForm):
    class Meta:
        model = QuestionResponse
        fields = ['response_text', 'selected_option']

QuestionResponseFormSet = forms.inlineformset_factory(
    AssignmentSubmission, QuestionResponse, form=QuestionResponseForm, extra=0, can_delete=False
)
