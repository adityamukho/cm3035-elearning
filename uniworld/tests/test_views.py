import pytest
from django.contrib.auth.models import User
from django.urls import reverse

from uniworld.model_factories import CourseFactory
from uniworld.models import Course


@pytest.fixture
def client():
    from django.test import Client
    return Client()

@pytest.fixture
def teacher():
    return User.objects.create_user(username='teacher', password='password')

@pytest.fixture
def student():
    return User.objects.create_user(username='student', password='password')

@pytest.fixture
def course(teacher):
    return CourseFactory.create(user=teacher, name='Test Course')

def test_heartbeat_view(client):
    response = client.get(reverse('heartbeat'))
    assert response.status_code == 200
    assert "alive" in response.content.decode()

def test_home_view(client):
    response = client.get(reverse('home'))
    assert response.status_code == 200
    assert 'home.html' in [t.name for t in response.templates]

def test_course_list_view(client, course):
    response = client.get(reverse('courses'))
    assert response.status_code == 200
    assert 'Test Course' in response.content.decode()

def test_course_detail_view(client, course):
    response = client.get(reverse('course', args=[course.pk]))
    assert response.status_code == 200
    assert 'Test Course' in response.content.decode()

def test_course_create_view_teacher(client, teacher):
    client.login(username='teacher', password='password')
    response = client.post(reverse('course-create'), {
        'name': 'New Course',
        'description': 'New Description'
    })
    assert response.status_code == 302  # Redirect after success
    assert Course.objects.filter(name='New Course').exists()

def test_course_create_view_student(client, student):
    client.login(username='student', password='password')
    response = client.post(reverse('course-create'), {
        'name': 'New Course',
        'description': 'New Description'
    })
    assert response.status_code == 403  # Forbidden

def test_course_update_view_teacher(client, teacher, course):
    client.login(username='teacher', password='password')
    response = client.post(reverse('course-update', args=[course.pk]), {
        'name': 'Updated Course',
        'description': 'Updated Description'
    })
    assert response.status_code == 302  # Redirect after success
    course.refresh_from_db()
    assert course.name == 'Updated Course'

def test_course_delete_view_teacher(client, teacher, course):
    client.login(username='teacher', password='password')
    response = client.post(reverse('course-delete', args=[course.pk]))
    assert response.status_code == 302  # Redirect after success
    assert not Course.objects.filter(pk=course.pk).exists()
