from django.contrib import admin
from django.urls import path, include

from . import views

app_name = "play_together"
urlpatterns = [
    # Redirect to login
    path("", views.index, name="index"),
    # Player site views/endpoints
    path("player/", views.PlayerDetail.as_view(), name="player-detail"),
    path("player/console/<int:pk>/toggle", views.toggle_owned_console, name="player-toggle-console"),
    # Game views
    path("game/<int:pk>/", views.GameDetail.as_view(), name="game-detail"),
    path("game/create/", views.GameCreate.as_view(), name="game-add"),
    path("game/<int:pk>/change/", views.GameUpdate.as_view(), name="game-change"),
    # Group views
    path("group/<int:pk>", views.group_view, name="group_view"),
]
