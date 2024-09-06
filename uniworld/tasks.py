from celery import shared_task
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from .models import Course, CourseMaterial, AssignmentSubmission

@shared_task
def notify_teacher_of_enrollment(course_id, student_id):
    User = get_user_model()
    try:
        course = Course.objects.get(id=course_id)
        student = User.objects.get(id=student_id)
        teacher = course.teacher

        send_mail(
            subject='New Enrollment in Your Course',
            message=f'{student.first_name} {student.last_name} has enrolled in your course "{course.name}".',
            from_email='no-reply@uniworld.example',
            recipient_list=[teacher.email],
            fail_silently=False,
        )
    except Course.DoesNotExist:
        print(f"Course with id {course_id} does not exist.")
    except User.DoesNotExist:
        print(f"User with id {student_id} does not exist.")

@shared_task
def notify_teacher_of_unenrollment(course_id, student_id):
    User = get_user_model()
    try:
        course = Course.objects.get(id=course_id)
        student = User.objects.get(id=student_id)
        teacher = course.teacher

        send_mail(
            subject='Student Left Your Course',
            message=f'{student.first_name} {student.last_name} has left your course "{course.name}".',
            from_email='no-reply@uniworld.example',
            recipient_list=[teacher.email],
            fail_silently=False,
        )
    except Course.DoesNotExist:
        print(f"Course with id {course_id} does not exist.")
    except User.DoesNotExist:
        print(f"User with id {student_id} does not exist.")

@shared_task
def notify_student_of_addition(course_id, student_id):
    User = get_user_model()
    try:
        course = Course.objects.get(id=course_id)
        student = User.objects.get(id=student_id)
        teacher = course.teacher

        send_mail(
            subject='You Have Been Added to a Course',
            message=f'You have been added to the course "{course.name}" by {teacher.first_name} {teacher.last_name}.',
            from_email='no-reply@uniworld.example',
            recipient_list=[student.email],
            fail_silently=False,
        )
    except Course.DoesNotExist:
        print(f"Course with id {course_id} does not exist.")
    except User.DoesNotExist:
        print(f"User with id {student_id} does not exist.")

@shared_task
def notify_student_of_removal(course_id, student_id):
    User = get_user_model()
    try:
        course = Course.objects.get(id=course_id)
        student = User.objects.get(id=student_id)
        teacher = course.teacher

        send_mail(
            subject='You Have Been Removed from a Course',
            message=f'You have been removed from the course "{course.name}" by {teacher.first_name} {teacher.last_name}.',
            from_email='no-reply@uniworld.example',
            recipient_list=[student.email],
            fail_silently=False,
        )
    except Course.DoesNotExist:
        print(f"Course with id {course_id} does not exist.")
    except User.DoesNotExist:
        print(f"User with id {student_id} does not exist.")

@shared_task
def notify_students_of_new_material(course_id, material_id):
    User = get_user_model()
    try:
        course = Course.objects.get(id=course_id)
        material = CourseMaterial.objects.get(id=material_id)
        students = course.students.all()

        for student in students:
            send_mail(
                subject='New Course Material Added',
                message=f'New material "{material.title}" has been added to the course "{course.name}".',
                from_email='no-reply@uniworld.example',
                recipient_list=[student.email],
                fail_silently=False,
            )
    except Course.DoesNotExist:
        print(f"Course with id {course_id} does not exist.")
    except CourseMaterial.DoesNotExist:
        print(f"CourseMaterial with id {material_id} does not exist.")
    except User.DoesNotExist:
        print(f"User does not exist.")

@shared_task
def notify_students_of_updated_material(course_id, material_id):
    User = get_user_model()
    try:
        course = Course.objects.get(id=course_id)
        material = CourseMaterial.objects.get(id=material_id)
        students = course.students.all()

        for student in students:
            send_mail(
                subject='Course Material Updated',
                message=f'The material "{material.title}" in the course "{course.name}" has been updated.',
                from_email='no-reply@uniworld.example',
                recipient_list=[student.email],
                fail_silently=False,
            )
    except Course.DoesNotExist:
        print(f"Course with id {course_id} does not exist.")
    except CourseMaterial.DoesNotExist:
        print(f"CourseMaterial with id {material_id} does not exist.")
    except User.DoesNotExist:
        print(f"User does not exist.")

@shared_task
def notify_teacher_of_assignment_submission(course_id, student_id, assignment_id):
    User = get_user_model()
    try:
        course = Course.objects.get(id=course_id)
        student = User.objects.get(id=student_id)
        teacher = course.teacher
        assignment = AssignmentSubmission.objects.get(id=assignment_id)

        send_mail(
            subject='New Assignment Submission',
            message=f'{student.first_name} {student.last_name} has submitted an assignment for your course "{course.name}".',
            from_email='no-reply@uniworld.example',
            recipient_list=[teacher.email],
            fail_silently=False,
        )
    except Course.DoesNotExist:
        print(f"Course with id {course_id} does not exist.")
    except User.DoesNotExist:
        print(f"User with id {student_id} does not exist.")
    except AssignmentSubmission.DoesNotExist:
        print(f"Assignment with id {assignment_id} does not exist.")


