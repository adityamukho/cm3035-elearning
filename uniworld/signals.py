from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import AssignmentSubmission, Course, CourseMaterial
from .tasks import (
    notify_student_of_graded_submission,
    notify_teacher_of_enrollment,
    notify_students_of_new_material,
    notify_students_of_updated_material
)
from chat.models import Room

@receiver(post_save, sender=AssignmentSubmission)
def submission_graded(sender, instance, created, **kwargs):
    if not created and instance.total_score is not None:
        notify_student_of_graded_submission.delay(instance.id)

@receiver(post_save, sender=Course)
def student_enrolled(sender, instance, created, **kwargs):
    if not created:
        # Check if a new student was added
        if instance.students.exists():
            latest_student = instance.students.latest('date_joined')
            notify_teacher_of_enrollment.delay(instance.id, latest_student.id)

@receiver(post_save, sender=CourseMaterial)
def material_added_or_updated(sender, instance, created, **kwargs):
    if created:
        notify_students_of_new_material.delay(instance.course.id, instance.id)
    else:
        notify_students_of_updated_material.delay(instance.course.id, instance.id)

@receiver(pre_save, sender=Course)
def create_course_chat_room(sender, instance, **kwargs):
    if not instance.pk and instance.chat_room is None:
        room = Room.objects.create(name=f"Chat for {instance.name}", creator=instance.teacher)
        instance.chat_room = room
