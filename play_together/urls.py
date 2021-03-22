from django.urls import path

from . import views

app_name = "play_together"
urlpatterns = [
    # Redirect to login
    path("", views.index, name="index"),
    # Toggling error
    path("toggle/error/", views.toggle_error, name="toggle-error"),
    # Player site views/endpoints
    path("player/", views.player_detail, name="player-detail"),
    path("player/console/<int:pk>/toggle", views.toggle_owned_console, name="player-toggle-console"),
    path("player/game/<int:game_pk>/console/<int:console_pk>/toggle", views.toggle_game_for_console,
         name="player-game-toggle-console"),
    path("player/game/add", views.player_add_game, name="player-game-add"),
    path("player/game/remove", views.player_remove_game, name="player-game-remove"),
    # Game views
    path("game/<int:pk>/", views.GameDetail.as_view(), name="game-detail"),
    path("game/create/", views.GameCreate.as_view(), name="game-add"),
    path("game/<int:pk>/change/", views.GameUpdate.as_view(), name="game-change"),
    # Group views
    path("group/<int:pk>", views.group_detail, name="group-detail"),
    path("group/<int:pk>/game/add", views.group_add_game, name="group-game-add"),
    path("group/<int:pk>/game/remove", views.group_remove_game, name="group-game-remove"),
]
