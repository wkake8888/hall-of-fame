import re
from django.test import TestCase, Client
from django.contrib.auth.models import User, AnonymousUser
from ..models import Hall, Video, VideoUserRelation
from ..views import dashboard


def create_hall(title, hall_user):
    return Hall.objects.create(title=title, user=hall_user)


class SignUpTests(TestCase):
    def test_get_signup(self):
        client = Client()
        response = client.get('/signup')
        self.assertEqual(response.status_code, 200)

    def test_post_signup(self):
        client = Client()
        params = {
            'username': 'tester',
            'email': 'test@...',
            'password1': 'top_secret',
            'password2': 'top_secret2'
        }
        response = client.post('/signup', params, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), 1)


class DashboardTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
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


class UpdateHallTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='tester', password='top_secret')
        cls.hall = Hall.objects.create(title='test title', user=cls.user)

    def test_get_update_hall(self):
        client = Client()
        client.force_login(self.user)
        response = client.get('/halloffame/' + str(self.hall.id) + '/update')
        self.assertContains(response, 'test title')

    def test_not_hall_manager_get(self):
        client = Client()
        not_hall_manager = User.objects.create(username='taro', password='hoge')
        client.force_login(not_hall_manager)
        response = client.get('/halloffame/' + str(self.hall.id) + '/update')
        self.assertEqual(response.status_code, 404)

    def test_post_update_hall(self):
        client = Client()
        client.force_login(self.user)
        params = {'title': 'updated title'}
        response = client.post('/halloffame/' + str(self.hall.id) + '/update', params, format='json')
        self.assertRedirects(response, '/dashboard', status_code=302, target_status_code=200, msg_prefix='', fetch_redirect_response=True)
        get_response = client.get('/halloffame/' + str(self.hall.id) + '/update')
        self.assertContains(get_response, 'updated title')


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


class AddVideoTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='tester', password='top_secret')
        cls.hall = Hall.objects.create(title='test title', user=cls.user)

    def test_not_hall_manager(self):
        not_hall_manager = User.objects.create(username='taro', password='hoge')
        client = Client()
        client.force_login(not_hall_manager)
        response = client.get('/halloffame/' + str(self.hall.id) + '/add_video')
        self.assertEqual(response.status_code, 404)

    def test_add_video_with_wrong_url(self):
        # No video at initial state
        self.assertEqual(Video.objects.count(), 0)

        # Try to add a video by wrong url
        client = Client()
        client.force_login(self.user)
        url = 'https://www.youtube.com/watch?v=K8hF7qQE5n'
        params = {
            'hall': self.hall,
            'url': url,
        }
        response = client.post('/halloffame/' + str(self.hall.id) + '/add_video', params, format='json')
        self.assertEqual(Video.objects.count(), 0)
        # self.assertRedirects(response, '/halloffame/' + str(self.hall.id), status_code=302, target_status_code=200, msg_prefix='', fetch_redirect_response=True)

    def test_add_video(self):
        # No video at initial state
        self.assertEqual(Video.objects.count(), 0)

        # Add a video
        client = Client()
        client.force_login(self.user)
        url = 'https://www.youtube.com/watch?v=K8hF7qQE5nQ'
        params = {
            'hall': self.hall,
            'url': url,
        }
        response = client.post('/halloffame/' + str(self.hall.id) + '/add_video', params, format='json')
        self.assertEqual(Video.objects.count(), 1)
        self.assertRedirects(response, '/halloffame/' + str(self.hall.id), status_code=302, target_status_code=200, msg_prefix='', fetch_redirect_response=True)


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
