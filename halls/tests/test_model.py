from django.test import TestCase
from halls.models import Hall, Video, VideoUserRelation
from django.contrib.auth.models import User

class HallModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='jacob', email='jacob@…', password='top_secret')

    def test_is_empty(self):
        saved_halls = Hall.objects.all()
        self.assertEqual(saved_halls.count(), 0)

    def test_is_one(self):
        hall = Hall(title="Anime", user=self.user)
        hall.save()
        saved_halls = Hall.objects.all()
        self.assertEqual(saved_halls.count(), 1)

    def test_saving_and_retrieving_post(self):
        hall = Hall()
        title = 'Tennis'
        hall.title = title
        hall.user = self.user
        hall.save()

        saved_halls = Hall.objects.all()
        actual_hall = saved_halls[0]

        self.assertEqual(actual_hall.title, title)
        self.assertEqual(actual_hall.user, self.user)