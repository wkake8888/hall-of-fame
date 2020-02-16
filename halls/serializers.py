from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Hall, Video, VideoUserRelation


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class HallSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hall
        fields = '__all__'


class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = '__all__'


class VideoUserRelationSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoUserRelation
        fields = '__all__'
