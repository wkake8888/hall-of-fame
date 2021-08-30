from django.test import TestCase, Client, RequestFactory
from django.test.utils import setup_test_environment
from django.contrib.auth.models import User
from django.urls import reverse
from ..models import Hall, Video, VideoUserRelation
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


class CreateHallTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.factory = RequestFactory()
        cls.user = User.objects.create_user(username='tester', password='top_secret')

    def test_create_success(self):
        # Initial states of DB
        # There is no record
        self.assertEqual(Hall.objects.count(), 0)

        # Create a Hall
        client = Client()
        client.login(username='tester', password='top_secret')
        params = {'title': 'test title'}
        response = client.post('/halloffame/create', params, format='json')
        self.assertEqual(Hall.objects.count(), 1)
        self.assertRedirects(response, '/dashboard', status_code=302, target_status_code=200, msg_prefix='', fetch_redirect_response=True)


class DetailHallTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='tester', password='top_secret')

    def test_access_with_correct_pk(self):
        hall = Hall.objects.create(title='test title', user=self.user)
        id = hall.id
        client = Client()
        response = client.get('/halloffame/' + str(id))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, hall.title)

    def test_access_with_wrong_pk(self):
        hall = Hall.objects.create(title='test title', user=self.user)
        id = hall.id + 1
        client = Client()
        response = client.get('/halloffame/' + str(id))
        self.assertEqual(response.status_code, 404)


class DeleteHallTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='tester', password='top_secret')
        cls.titles = ['title A', 'title B', 'title C']
        for x in cls.titles:
            Hall.objects.create(title=x, user=cls.user)

    def test_delete_hall(self):
        # There are 3 records at initial state
        self.assertEqual(Hall.objects.count(), 3)

        # Delete a hall from DB
        client = Client()
        client.login(username='tester', password='top_secret')
        hall_a = Hall.objects.get(title=self.titles[0])
        response = client.post('/halloffame/' + str(hall_a.id) + '/delete')
        self.assertEqual(Hall.objects.count(), 2)
        self.assertRedirects(response, '/dashboard', status_code=302, target_status_code=200, msg_prefix='', fetch_redirect_response=True)


class DeleteVideoTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='tester', password='top_secret')
        cls.hall = Hall.objects.create(title='test title', user=cls.user)
        video_user_relation = VideoUserRelation.objects.all()
        cls.video = Video.objects.create(title='test title', url='https://www.hoge.com', youtube_id='id', hall=cls.hall)
        cls.video.liker.set(video_user_relation)

    def test_delete_video(self):
        # There is a video at initial state
        self.assertEqual(Video.objects.count(), 1)

        # Delete a Video from DB
        video = Video.objects.get()
        client = Client()
        client.login(username='tester', password='top_secret')
        response = client.post('/halloffame/' + str(video.id) + '/delete')
        self.assertEqual(Video.objects.count(), 0)
        self.assertRedirects(response, '/dashboard', status_code=302, target_status_code=200, msg_prefix='', fetch_redirect_response=True)
