import re
from django.test import TestCase, Client
from django.contrib.auth.models import User, AnonymousUser
from unittest.mock import patch

from django.test.testcases import TransactionTestCase
from ..models import Hall, Video, VideoUserRelation
from ..views import dashboard


class SignUpTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()

    def test_get_signup(self):
        response = self.client.get('/signup')
        self.assertEqual(response.status_code, 200)

    def test_post_signup(self):
        params = {
            'username': 'hogetaro',
            'email': 'hoge@gmail.com',
            'password1': 'hoge8888',
            'password2': 'hoge8888'
        }
        response = self.client.post('/signup', params, format='json')
        self.assertRedirects(response, '/dashboard', status_code=302, target_status_code=200, msg_prefix='', fetch_redirect_response=True)
        self.assertEqual(User.objects.count(), 1)


class DashboardTests(TransactionTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='tester', password='top_secret')
        cls.client = Client()

    def test_no_hall(self):
        self.client.login(username='tester', password='top_secret')
        response = self.client.get('/dashboard')
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['halls'], [])

    def test_one_hall(self):
        self.client.login(username='tester', password='top_secret')
        hall = Hall.objects.create(title='title', user=self.user)
        response = self.client.get('/dashboard')
        repr_hall = repr(hall)
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['halls'], [repr_hall])


class CreateHallTests(TransactionTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='tester', password='top_secret')
        cls.client = Client()

    def test_create_success(self):
        # Initial states of DB
        # There is no record
        self.assertEqual(Hall.objects.count(), 0)

        # Create a Hall
        self.client.login(username='tester', password='top_secret')
        params = {'title': 'test title'}
        response = self.client.post('/halloffame/create', params, format='json')
        self.assertEqual(Hall.objects.count(), 1)
        self.assertRedirects(response, '/dashboard', status_code=302, target_status_code=200, msg_prefix='', fetch_redirect_response=True)


class DetailHallTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='tester', password='top_secret')
        cls.client = Client()

    def test_access_with_correct_pk(self):
        hall = Hall.objects.create(title='test title', user=self.user)
        id = hall.id
        response = self.client.get('/halloffame/' + str(id))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, hall.title)

    def test_access_with_wrong_pk(self):
        hall = Hall.objects.create(title='test title', user=self.user)
        id = hall.id + 1
        response = self.client.get('/halloffame/' + str(id))
        self.assertEqual(response.status_code, 404)


class UpdateHallTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='tester', password='top_secret')
        cls.hall = Hall.objects.create(title='test title', user=cls.user)
        cls.client = Client()

    def test_get_update_hall(self):
        self.client.force_login(self.user)
        response = self.client.get('/halloffame/' + str(self.hall.id) + '/update')
        self.assertContains(response, 'test title')

    def test_not_hall_manager_get(self):
        not_hall_manager = User.objects.create(username='taro', password='hoge')
        self.client.force_login(not_hall_manager)
        response = self.client.get('/halloffame/' + str(self.hall.id) + '/update')
        self.assertEqual(response.status_code, 404)

    def test_post_update_hall(self):
        self.client.force_login(self.user)
        params = {'title': 'updated title'}
        response = self.client.post('/halloffame/' + str(self.hall.id) + '/update', params, format='json')
        self.assertRedirects(response, '/dashboard', status_code=302, target_status_code=200, msg_prefix='', fetch_redirect_response=True)
        get_response = self.client.get('/halloffame/' + str(self.hall.id) + '/update')
        self.assertContains(get_response, 'updated title')


class DeleteHallTests(TransactionTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='tester', password='top_secret')
        cls.titles = ['title A', 'title B', 'title C']
        for x in cls.titles:
            Hall.objects.create(title=x, user=cls.user)
        cls.client = Client()

    def test_delete_hall(self):
        # There are 3 records at initial state
        self.assertEqual(Hall.objects.count(), 3)

        # Delete a hall from DB
        self.client.login(username='tester', password='top_secret')
        hall_a = Hall.objects.get(title=self.titles[0])
        response = self.client.post('/halloffame/' + str(hall_a.id) + '/delete')
        self.assertEqual(Hall.objects.count(), 2)
        self.assertRedirects(response, '/dashboard', status_code=302, target_status_code=200, msg_prefix='', fetch_redirect_response=True)


class AddVideoTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='tester', password='top_secret')
        cls.hall = Hall.objects.create(title='test title', user=cls.user)
        cls.client = Client()

    def test_not_hall_manager(self):
        not_hall_manager = User.objects.create(username='taro', password='hoge')
        self.client.force_login(not_hall_manager)
        response = self.client.get('/halloffame/' + str(self.hall.id) + '/add_video')
        self.assertEqual(response.status_code, 404)

    def test_add_video_with_wrong_url(self):
        # No video at initial state
        self.assertEqual(Video.objects.count(), 0)

        # Try to add a video by wrong url
        self.client.force_login(self.user)
        url = 'https://www.youtube.com/watch?v=K8hF7qQE5n'
        params = {
            'hall': self.hall,
            'url': url,
        }
        response = self.client.post('/halloffame/' + str(self.hall.id) + '/add_video', params, format='json')
        self.assertEqual(Video.objects.count(), 0)
        # self.assertRedirects(response, '/halloffame/' + str(self.hall.id), status_code=302, target_status_code=200, msg_prefix='', fetch_redirect_response=True)

    def test_add_video(self):
        # No video at initial state
        self.assertEqual(Video.objects.count(), 0)

        # Add a video
        self.client.force_login(self.user)
        url = 'https://www.youtube.com/watch?v=K8hF7qQE5nQ'
        params = {
            'hall': self.hall,
            'url': url,
        }
        response = self.client.post('/halloffame/' + str(self.hall.id) + '/add_video', params, format='json')
        self.assertEqual(Video.objects.count(), 1)
        self.assertRedirects(response, '/halloffame/' + str(self.hall.id), status_code=302, target_status_code=200, msg_prefix='', fetch_redirect_response=True)


class DeleteVideoTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='tester', password='top_secret')
        cls.hall = Hall.objects.create(title='test title', user=cls.user)
        video_user_relation = VideoUserRelation.objects.all()
        cls.video = Video.objects.create(title='test title', url='https://www.youtube.com/watch?v=K8hF7qQE5nQ', youtube_id='id', hall=cls.hall)
        cls.video.liker.set(video_user_relation)

    def test_delete_video(self):
        # There is a video at initial state
        self.assertEqual(Video.objects.count(), 1)
        self.assertEqual(Hall.objects.count(), 1)

        # Delete a Video from DB
        client = Client()
        client.force_login(self.user)
        response = client.post('/halloffame/' + str(self.video.id) + '/delete')
        self.assertEqual(Video.objects.count(), 0)
        self.assertRedirects(response, '/dashboard', status_code=302, target_status_code=200, msg_prefix='', fetch_redirect_response=True)
