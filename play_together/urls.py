from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

app_name = "play_together"
urlpatterns = [
    path("", views.index, name="index"),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="play_together/login.html"),
        name="login",
    ),
    path("profile/", views.profile, name="profile"),
    path("group/<int:pk>", views.group_view, name="group_view"),
    path("game/<int:pk>/", views.GameDetail.as_view(), name="game-detail"),
    path("game/create/", views.GameCreate.as_view(), name="game-add"),
    path("game/<int:pk>/change/", views.GameUpdate.as_view(), name="game-change"),
]
