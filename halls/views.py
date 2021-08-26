from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth import authenticate, login
from .models import Hall, Video, VideoUserRelation
from .forms import SingupForm, VideoForm, SearchForm
from django.http import Http404, JsonResponse
from django.contrib.auth.models import User
import urllib
import requests
from django.forms.utils import ErrorList
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django_filters import rest_framework as filters
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework import viewsets, authentication, permissions, status
from rest_framework.views import APIView
from .serializers import UserSerializer, VideoUserRelationSerializer, HallSerializer, VideoSerializer


YOUTUBE_API_KEY = 'AIzaSyDiCnsnhoOLn0xMhpbyU8RjNmMbrrypnI4'


@login_required
def home(request):
    recent_halls = Hall.objects.all().order_by('-id')[:3]
    popular_halls = [Hall.objects.get(pk=2), Hall.objects.get(pk=3), Hall.objects.get(pk=4)]
    return render(request, 'halls/home.html', {'recent_halls': recent_halls, 'popular_halls': popular_halls})


@login_required
def dashboard(request):
    halls = Hall.objects.filter(user=request.user)
    return render(request, 'halls/dashboard.html', {'halls': halls})


@login_required
def add_video(request, pk):
    form = VideoForm()
    search_form = SearchForm()
    hall = Hall.objects.get(pk=pk)
    if not hall.user == request.user:
        raise Http404
    if request.method == 'POST':
        form = VideoForm(request.POST)
        if form.is_valid():
            video = Video()
            video.hall = hall
            video.url = form.cleaned_data['url']
            parsed_url = urllib.parse.urlparse(video.url)
            video_id = urllib.parse.parse_qs(parsed_url.query).get('v')
            if video_id:
                video.youtube_id = video_id[0]
                response = requests.get(f'https://www.googleapis.com/youtube/v3/videos?part=snippet&id={ video_id[0] }&key={ YOUTUBE_API_KEY }')
                json = response.json()
                title = json['items'][0]['snippet']['title']
                video.title = title
                video.save()
                return redirect('detail_hall', pk)
            else:
                errors = form._errors.setdefault('url', ErrorList())
                errors.append('Needs to be a YouTube URL')

    return render(request, 'halls/add_video.html', {'form': form, 'search_form': search_form, 'hall': hall})


@login_required
def video_search(request):
    search_form = SearchForm(request.GET)
    if search_form.is_valid():
        search_form.cleaned_data['search_term']
        encoded_search_term = urllib.parse.quote(search_form.cleaned_data['search_term'])
        response = requests.get(f'https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults=6&q={ encoded_search_term }&key={ YOUTUBE_API_KEY }')
        return JsonResponse(response.json())
    else:
        return JsonResponse({'error': 'Not able to validate form'})


class SignUp(generic.CreateView):
    form_class = SingupForm
    success_url = reverse_lazy('dashboard')
    template_name = 'registration/signup.html'

    # This method is called when valid form data has been POSTed.
    # It should return an HttpResponse.
    def form_valid(self, form):
        view = super(SignUp, self).form_valid(form)
        username, password = form.cleaned_data.get('username'), form.cleaned_data.get('password1')
        user = authenticate(username=username, password=password)
        login(self.request, user)
        # Send email
        html_message = render_to_string(
            'registration/send_welcome_mail.html',
            {
                'username': user.username,
            }
        )

        send_mail('Welcome to Hall of Fame', html_message, 'EMAIL_HOST_USER', [user.email])

        return view


class CreateHall(LoginRequiredMixin, generic.CreateView):
    model = Hall
    fields = ['title']
    template_name = 'halls/create_hall.html'
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        form.instance.user = self.request.user
        super(CreateHall, self).form_valid(form)
        return redirect('dashboard')


class DetailHall(generic.DetailView):
    model = Hall
    template_name = 'halls/detail_hall.html'


class UpdateHall(LoginRequiredMixin, generic.UpdateView):
    model = Hall
    template_name = 'halls/update_hall.html'
    fields = ['title']
    success_url = reverse_lazy('dashboard')

    def get_object(self):
        hall = super(UpdateHall, self).get_object()
        if not hall.user == self.request.user:
            raise Http404
        return hall


class DeleteHall(LoginRequiredMixin, generic.DeleteView):
    model = Hall
    template_name = 'halls/delete_hall.html'
    success_url = reverse_lazy('dashboard')

    def get_object(self):
        hall = super(DeleteHall, self).get_object()
        if not hall.user == self.request.user:
            raise Http404
        return hall


class DeleteVideo(LoginRequiredMixin, generic.DeleteView):
    model = Video
    template_name = 'halls/delete_video.html'
    success_url = reverse_lazy('dashboard')

    def get_object(self):
        video = super(DeleteVideo, self).get_object()
        if not video.hall.user == self.request.user:
            raise Http404
        return video


class VideoUserRelationViewSet(viewsets.ModelViewSet):
    queryset = VideoUserRelation.objects.all()
    serializer_class = VideoUserRelationSerializer


class LikeFilter(filters.FilterSet):
    class Meta:
        model = VideoUserRelation
        fields = '__all__'


class LikeButton(APIView):
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = VideoUserRelationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        video_id = serializer.validated_data['video']
        if VideoUserRelation.objects.filter(liker=request.user, video=video_id).exists():
            print('already exist so delete the object')
            get_object_or_404(VideoUserRelation, liker=request.user, video=video_id).delete()
        else:
            print('new user')
            serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request):
        pk = request.query_params.get('pk')
        filter_set = LikeFilter(request.query_params, queryset=VideoUserRelation.objects.filter(video=pk))
        if not filter_set.is_valid():
            raise ValidationError(filter_set.errors)
        serializer = VideoUserRelationSerializer(instance=filter_set.qs, many=True)
        print(filter_set.qs)
        return Response(serializer.data, status.HTTP_200_OK)
