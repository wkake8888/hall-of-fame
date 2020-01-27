from .models import Video
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db import models

from django import forms


class SingupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email']
        labels = {'username': 'User Name', 'email': 'Email'}


class VideoForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ['url']
        labels = {'url': 'YouTube URL'}


class SearchForm(forms.Form):
    search_term = forms.CharField(max_length=255, label='Search for a Video')
