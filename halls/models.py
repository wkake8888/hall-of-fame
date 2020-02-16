from django.db import models
from django.contrib.auth.models import User


class Hall(models.Model):
    title = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class Video(models.Model):
    title = models.CharField(max_length=255)
    url = models.URLField()
    youtube_id = models.CharField(max_length=255)
    hall = models.ForeignKey(Hall, on_delete=models.CASCADE)
    liker = models.ManyToManyField(User, through='VideoUserRelation')


class VideoUserRelation(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    liker = models.ForeignKey(User, on_delete=models.CASCADE)
