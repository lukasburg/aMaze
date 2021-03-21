from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.detail import DetailView

from .models import Game, Console, Player, PlayerGroup
# from .forms import PlayerInlinesForm


def index(request):
    return redirect("play_together:player-detail")


class GameDetail(DetailView):
    model = Game


class GameCreate(CreateView):
    model = Game
    fields = ['name', 'price', 'available_on', 'multiplayer_count', 'crossplay_support', 'comment']


class GameUpdate(UpdateView):
    model = Game
    fields = ['name', 'price', 'available_on', 'multiplayer_count', 'crossplay_support', 'comment']


@method_decorator(login_required, name='dispatch')
class PlayerDetail(DetailView):
    model = Player

    def get_object(self, queryset=None):
        return self.request.user.player

    def get_context_data(self, **kwargs):
        player = self.get_object()
        context = super().get_context_data(**kwargs)
        context['addable_games'] = Game.objects.exclude(
            id__in=player.games.values_list('id')
        )
        context['addable_consoles'] = Console.objects.exclude(
            id__in=player.consoles.values_list('id')
        ).all()
        print(context)
        return context


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
