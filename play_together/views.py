from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Player, PlayerGroup


def index(request):
    return redirect("play_together:profile")


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
def group_view(request, group_id):
    group = get_object_or_404(PlayerGroup, id=group_id)
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
