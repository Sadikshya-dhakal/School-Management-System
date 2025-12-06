from django.test import TestCase,Client
from django.contrib.auth import get_user_model
from .models import student

CustomUser = get_user_model()

class CustomUserModelTest(TestCase):
    def test_create_user(self):
        user = CustomUser.objects.create_user(
            email='test@example.com',
            password='testpass123',
            user_type=1
        )
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('testpass123'))
        self.assertEqual(user.user_type, 1)

class StudentModelTest(TestCase):
    def test_create_student(self):
        user = CustomUser.objects.create_user(
            email='student@example.com',
            password='password',
            user_type=3
        )
        student_obj = student.objects.create(
            admin=user,
            address='123 Main Street'
        )
        self.assertEqual(student_obj.admin.email, 'student@example.com')
        self.assertEqual(student_obj.address, '123 Main Street')


class LoginViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create_user(
            email='admin@example.com',
            password='adminpass',
            user_type=1
        )

    def test_login_valid_user(self):
        response = self.client.post('/doLogin/', {
            'email': 'admin@example.com',
            'password': 'adminpass'
        })
        self.assertEqual(response.status_code, 302)  # redirect

    def test_login_invalid_user(self):
        response = self.client.post('/doLogin/', {
            'email': 'fake@example.com',
            'password': 'wrongpass'
        })
        self.assertEqual(response.status_code, 200)  # login page reload
