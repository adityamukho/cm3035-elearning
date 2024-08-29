import pytest
from django.contrib.auth.models import User, Group
from django.urls import reverse

from uniworld.model_factories import CourseFactory
from uniworld.models import Course


@pytest.fixture
def client():
    from django.test import Client
    return Client()


@pytest.fixture
def group_teachers():
    return Group.objects.create(name='teachers')


@pytest.fixture
def group_students():
    return Group.objects.create(name='students')


@pytest.fixture
def teacher(group_teachers):
    teacher = User.objects.create_user(username='teacher', password='password')
    teacher.groups.add(group_teachers)

    return teacher


@pytest.fixture
def student(group_students):
    student = User.objects.create_user(username='student', password='password')
    student.groups.add(group_students)

    return student


@pytest.fixture
def course(teacher):
    return CourseFactory.create(teacher=teacher, name='Test Course')


def test_heartbeat_view(client):
    response = client.get(reverse('heartbeat'))
    assert response.status_code == 200
    assert "alive" in response.content.decode()


def test_home_view(client):
    response = client.get(reverse('home'))
    assert response.status_code == 200
    assert 'home.html' in [t.name for t in response.templates]


@pytest.mark.django_db
def test_course_list_view(client, course):
    response = client.get(reverse('courses'))
    assert response.status_code == 200
    assert 'Test Course' in response.content.decode()


@pytest.mark.django_db
def test_course_detail_view(client, course):
    response = client.get(reverse('course', args=[course.pk]))
    assert response.status_code == 200
    assert 'Test Course' in response.content.decode()


@pytest.mark.django_db
def test_course_create_view_teacher(client, teacher):
    client.login(username='teacher', password='password')
    response = client.post(reverse('course-create'), {
        'name': 'New Course',
        'description': 'New Description'
    })
    assert response.status_code == 302  # Redirect after success
    assert Course.objects.filter(name='New Course').exists()


@pytest.mark.django_db
def test_course_create_view_student(client, student):
    client.login(username='student', password='password')
    response = client.post(reverse('course-create'), {
        'name': 'New Course',
        'description': 'New Description'
    })
    assert response.status_code == 403  # Forbidden


@pytest.mark.django_db
def test_course_update_view_teacher(client, teacher, course):
    client.login(username='teacher', password='password')
    response = client.post(reverse('course-update', args=[course.pk]), {
        'name': 'Updated Course',
        'description': 'Updated Description'
    })
    assert response.status_code == 302  # Redirect after success
    course.refresh_from_db()
    assert course.name == 'Updated Course'


@pytest.mark.django_db
def test_course_delete_view_teacher(client, teacher, course):
    client.login(username='teacher', password='password')
    response = client.post(reverse('course-delete', args=[course.pk]))
    assert response.status_code == 302  # Redirect after success
    assert not Course.objects.filter(pk=course.pk).exists()
