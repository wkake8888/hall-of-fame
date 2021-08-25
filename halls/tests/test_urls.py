from django.test import TestCase
from django.urls import resolve
from ..views import SignUp, home, dashboard, CreateHall, DetailHall, \
    UpdateHall, DeleteHall, add_video, video_search, DeleteVideo, LikeButton
from django.contrib.auth import views as auth_views


class TestUrls(TestCase):
    def test_home_routing(self):
        view = resolve('/')
        self.assertEqual(view.func, home)

    def test_dashboard_routing(self):
        view = resolve('/dashboard')
        self.assertEqual(view.func, dashboard)

    # AUTH
    def test_signup_routing(self):
        view = resolve('/signup')
        self.assertEqual(view.func.view_class, SignUp)

    def test_login_routing(self):
        view = resolve('/login')
        self.assertEqual(view.func.view_class, auth_views.LoginView)

    def test_logout_routing(self):
        view = resolve('/logout')
        self.assertEqual(view.func.view_class, auth_views.LogoutView)

    # Hall
    def test_create_hall_routing(self):
        view = resolve('/halloffame/create')
        self.assertEqual(view.func.view_class, CreateHall)

    def test_detail_hall_routing(self):
        view = resolve('/halloffame/2')
        self.assertEqual(view.func.view_class, DetailHall)

    def test_update_hall_routing(self):
        view = resolve('/halloffame/2/update')
        self.assertEqual(view.func.view_class, UpdateHall)

    def test_delete_hall_routing(self):
        view = resolve('/halloffame/2/delete')
        self.assertEqual(view.func.view_class, DeleteHall)

    # Video
    def test_add_video_routing(self):
        view = resolve('/halloffame/2/add_video')
        self.assertEqual(view.func, add_video)

    def test_video_search_routing(self):
        view = resolve('/video/search')
        self.assertEqual(view.func, video_search)

    def test_delete_video_routing(self):
        view = resolve('/video/2/delete')
        self.assertEqual(view.func.view_class, DeleteVideo)

    def test_like_button_routing(self):
        view = resolve('/api/like_btn/')
        self.assertEqual(view.func.view_class, LikeButton)
