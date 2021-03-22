from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView
from django_http_exceptions import HTTPExceptions

from .decorators import login_required_return_denied
from .models import Game, Console, Player, PlayerGroup


def index(request):
    return redirect("play_together:player-detail")


def toggle_error(request):
    context = {
        'next': request.GET.get('next', reverse('play_together:player-detail', ))
    }
    return render(request, "play_together/toggle-error.html", context)


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
        player = self.object
        context = super().get_context_data(**kwargs)
        context['greet'] = self.request.GET.get('greet', False) == "True"
        context['error_reload'] = self.request.POST.get('error-reload', False) == "True"
        context['addable_games'] = Game.objects.exclude(
            id__in=player.games.values_list('id')
        )
        context['consoles'] = Console.objects.all()
        return context


def toggle_many_to_many(instance_one_class_two_set, instance_two, expected_set_state):
    current_state = instance_one_class_two_set.filter(id=instance_two.id).exists()
    if expected_set_state == current_state:
        raise HTTPExceptions.CONFLICT.with_content(
            f"Conflicting states. Client tried to set status {instance_two} to {expected_set_state}, "
            "which was already set on server. Refresh site!")
    if expected_set_state is True:
        instance_one_class_two_set.add(instance_two)
    else:
        instance_one_class_two_set.remove(instance_two)


@require_http_methods(['POST'])
@login_required_return_denied
def toggle_owned_console(request, pk):
    console = get_object_or_404(Console, pk=pk)
    player = request.user.player
    set_state = request.POST['set_state'] == 'true'
    toggle_many_to_many(player.consoles, console, set_state)
    return HttpResponse(status=200)


@require_http_methods(['POST'])
@login_required_return_denied
def toggle_game_for_console(request, game_pk, console_pk):
    game = get_object_or_404(Game, pk=game_pk)
    console = get_object_or_404(Console, pk=console_pk)
    player = request.user.player
    set_state = request.POST['set_state'] == 'true'
    if not player.ownedgame_set.filter(game_id=game).exists():
        raise HTTPExceptions.CONFLICT.with_content(
            "Conflicting states. "
            f"Client tried to toggle for game he does not have set to owned {game} ({player.ownedgame_set.all()})"
            "which was already set on server. Refresh site!")
    toggle_many_to_many(player.ownedgame_set.filter(game_id=game).first().consoles, console, set_state)
    return HttpResponse(status=200)


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
    context = {
        "group": group,
        "players": players,
        "ordered_games": games,
    }
    return render(request, "play_together/group_view.html", context)
