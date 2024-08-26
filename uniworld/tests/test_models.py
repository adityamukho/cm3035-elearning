import pytest
from django.contrib.auth.models import User, Group

from uniworld.model_factories import CourseFactory


@pytest.fixture
def teacher_group(db):
    group, created = Group.objects.get_or_create(name='teachers')
    return group

@pytest.fixture
def teacher(db, teacher_group):
    user = User.objects.create_user(username='teacher', password='password')
    user.groups.add(teacher_group)
    return user

@pytest.fixture
def student(db):
    return User.objects.create_user(username='student', password='password')

@pytest.fixture
def course(teacher):
    return CourseFactory.create(user=teacher, name='Test Course')

def test_course_creation(course):
    assert course.name == 'Test Course'
    assert course.user.username == 'teacher'

def test_teacher_can_add_course(teacher):
    assert teacher.has_perm('uniworld.add_course')

def test_student_cannot_add_course(student):
    assert not student.has_perm('uniworld.add_course')

def test_teacher_can_change_own_course(teacher, course):
    assert teacher.has_perm('uniworld.change_course', course)

def test_teacher_cannot_change_others_course(teacher, student):
    other_course = CourseFactory.create(user=student, name='Other Course')
    assert not teacher.has_perm('uniworld.change_course', other_course)

def test_teacher_can_delete_own_course(teacher, course):
    assert teacher.has_perm('uniworld.delete_course', course)

def test_teacher_cannot_delete_others_course(teacher, student):
    other_course = CourseFactory.create(user=student, name='Other Course')
    assert not teacher.has_perm('uniworld.delete_course', other_course)
