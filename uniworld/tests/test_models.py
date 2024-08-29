import pytest
from django.contrib.auth.models import User, Group

from uniworld.model_factories import CourseFactory

@pytest.mark.django_db
@pytest.fixture
def teachers_group():
    group, created = Group.objects.get_or_create(name='teachers')
    return group

@pytest.mark.django_db
@pytest.fixture
def teacher(teachers_group):
    user = User.objects.create_user(username='teacher', password='password')
    user.groups.add(teachers_group)
    return user

@pytest.mark.django_db
@pytest.fixture
def student():
    return User.objects.create_user(username='student', password='password')

@pytest.mark.django_db
@pytest.fixture
def course(teacher):
    return CourseFactory.create(teacher=teacher, name='Test Course')

@pytest.mark.django_db
def test_course_creation(course):
    assert course.name == 'Test Course'
    assert course.teacher.username == 'teacher'

@pytest.mark.django_db
def test_teacher_can_add_course(teacher):
    assert teacher.has_perm('uniworld.add_course')

@pytest.mark.django_db
def test_student_cannot_add_course(student):
    assert not student.has_perm('uniworld.add_course')

@pytest.mark.django_db
def test_teacher_can_change_own_course(teacher, course):
    assert teacher.has_perm('uniworld.change_course', course)

@pytest.mark.django_db
def test_teacher_cannot_change_others_course(teacher, student):
    other_course = CourseFactory.create(teacher=student, name='Other Course')
    assert not teacher.has_perm('uniworld.change_course', other_course)

@pytest.mark.django_db
def test_teacher_can_delete_own_course(teacher, course):
    assert teacher.has_perm('uniworld.delete_course', course)

@pytest.mark.django_db
def test_teacher_cannot_delete_others_course(teacher, student):
    other_course = CourseFactory.create(teacher=student, name='Other Course')
    assert not teacher.has_perm('uniworld.delete_course', other_course)
