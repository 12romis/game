from django.urls import path, include
from . import views

urlpatterns = [
    path('login', views.login, name='game_login'),
    path('signup', views.signup, name='game_signup'),
    path('profile', views.profile, name='game_profile'),
    path('check_code', views.check_code, name='game_check_code'),
    path('set_score', views.set_score, name='game_set_score'),
    path('get_rating', views.get_rating, name='game_get_rating'),
]
