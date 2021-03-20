from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.detail import DetailView
from .models import Game, Player, PlayerGroup


def index(request):
    return redirect("play_together:profile")


class GameDetail(DetailView):
    model = Game


class GameCreate(CreateView):
    model = Game
    fields = ['name', 'price', 'available_on', 'multiplayer_count', 'crossplay_support', 'comment']


class GameUpdate(UpdateView):
    model = Game
    fields = ['name', 'price', 'available_on', 'multiplayer_count', 'crossplay_support', 'comment']


# Create your views here.
@login_required
def profile(request):
    logged_in = Player.objects.get(user=request.user)
    users_groups = logged_in.playergroup_set.all()
    context = {
        "user": logged_in,
        "groups": users_groups,
    }
    return render(request, "play_together/profile.html", context)


@login_required
def group_view(request, pk):
    group = get_object_or_404(PlayerGroup, id=pk)
    if not request.user.player.is_part_of_group(group):
        return redirect(f"/login?next={request.path}")

    players = group.players.all()
    games = [
        (
            game,
            [
                [owned_game.console for owned_game in player.ownedgames_set.filter(game=game)]
                for player in players
            ]
        )
        for game in group.watched_games.all()
    ]
    print(games)
    context = {
        "group": group,
        "players": players,
        "ordered_games": games,
    }
    return render(request, "play_together/group_view.html", context)
