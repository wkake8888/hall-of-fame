from django.test import TestCase
from halls.models import Hall, Video, VideoUserRelation
from django.contrib.auth.models import User

class HallModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='taro', email='taro@…', password='top_secret')

    def test_is_empty(self):
        saved_halls = Hall.objects.all()
        self.assertEqual(saved_halls.count(), 0)

    def test_is_one(self):
        hall = Hall(title="Anime", user=self.user)
        hall.save()
        saved_halls = Hall.objects.all()
        self.assertEqual(saved_halls.count(), 1)

    def test_saving_and_retrieving_hall(self):
        hall = Hall()
        title = 'Tennis'
        hall.title = title
        hall.user = self.user
        hall.save()

        saved_halls = Hall.objects.all()
        actual_hall = saved_halls[0]

        self.assertEqual(actual_hall.title, title)
        self.assertEqual(actual_hall.user, self.user)


class VideoModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='taro', email='taro@…', password='top_secret')
        self.hall = Hall(title='Sports', user=self.user)
        self.hall.save()

    def test_is_empty(self):
        saved_videos = Video.objects.all()
        self.assertEqual(saved_videos.count(), 0)

    def test_is_one(self):
        video = Video(title='test title', url='https://www.youtube.com/watch?v=K8hF7qQE5nQ&list=LLRdrrwPIQqhSvZ7F-W2A_rg&index=5&t=0s', youtube_id='K8hF7qQE5nQ', hall=self.hall)
        video.save()
        saved_videos = Video.objects.all()
        self.assertEqual(saved_videos.count(), 1)

    def test_saving_and_retrieving_video(self):
        title = 'test title'
        url = 'https://www.youtube.com/watch?v=K8hF7qQE5nQ&list=LLRdrrwPIQqhSvZ7F-W2A_rg&index=5&t=0s'
        youtube_id = 'K8hF7qQE5nQ'
        video = Video(title='test title', url='https://www.youtube.com/watch?v=K8hF7qQE5nQ&list=LLRdrrwPIQqhSvZ7F-W2A_rg&index=5&t=0s', youtube_id='K8hF7qQE5nQ', hall=self.hall)
        video.save()

        saved_videos = Video.objects.all()
        actual_video = saved_videos[0]

        self.assertEqual(actual_video.title, title)
        self.assertEqual(actual_video.url, url)
        self.assertEqual(actual_video.youtube_id, youtube_id)
        self.assertEqual(actual_video.hall, self.hall)


class VideoUserRelationModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='taro', email='taro@…', password='top_secret')
        self.user.save()
        self.hall = Hall(title='Sports', user=self.user)
        self.hall.save()
        self.video = Video(title='test title', url='https://www.youtube.com/watch?v=K8hF7qQE5nQ&list=LLRdrrwPIQqhSvZ7F-W2A_rg&index=5&t=0s', youtube_id='K8hF7qQE5nQ', hall=self.hall)
        self.video.save()

    def test_is_empty(self):
        saved_video_user_relation = VideoUserRelation.objects.all()
        self.assertEqual(saved_video_user_relation.count(), 0)

    def test_is_one(self):
        video_user_relation = VideoUserRelation(video=self.video, liker=self.user)
        video_user_relation.save()
        saved_video_user_relation = VideoUserRelation.objects.all()
        self.assertEqual(saved_video_user_relation.count(), 1)

    def test_saving_and_retrieving_video_user_relation(self):
        video_user_relation = VideoUserRelation(video=self.video, liker=self.user)
        video_user_relation.save()

        saved_video_user_relation = VideoUserRelation.objects.all()
        actual_video_user_relation = saved_video_user_relation[0]
        self.assertEqual(actual_video_user_relation.video, self.video)
        self.assertEqual(actual_video_user_relation.liker, self.user)



