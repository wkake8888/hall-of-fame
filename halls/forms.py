from .models import Video
from django.db import models

from django import forms


class VideoForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ['url']
        labels = {'url': 'YouTube URL'}


class SearchForm(forms.Form):
    search_term = forms.CharField(max_length=255, label='Search for a Video')
