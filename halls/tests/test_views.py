from django.test import TestCase, Client, RequestFactory
from django.test.utils import setup_test_environment
from django.contrib.auth.models import User
from ..models import Hall
from ..views import dashboard


def create_hall(title, hall_user):
    return Hall.objects.create(title=title, user=hall_user)


class DashboardTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.factory = RequestFactory()
        cls.user = User.objects.create_user(username='tester', password='top_secret')

    def test_no_hall(self):
        client = Client()
        client.login(username='tester', password='top_secret')
        response = client.get('/dashboard')
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['halls'], [])

    def test_one_hall(self):
        client = Client()
        client.login(username='tester', password='top_secret')
        hall = Hall(title='title', user=self.user)
        hall.save()
        response = client.get('/dashboard')
        repr_hall = repr(hall)
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['halls'], [repr_hall])
