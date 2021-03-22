from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.decorators.http import require_http_methods
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView
from django_http_exceptions import HTTPExceptions

from .decorators import login_required_return_denied
from .forms import PlayerToggleGameForm, GroupToggleGameForm
from .models import Game, OwnedGame, Console, PlayerGroup


def index(request):
    return redirect("play_together:player-detail")


def toggle_error(request):
    context = {
        'next': request.GET.get('next', reverse('play_together:player-detail', ))
    }
    return render(request, "play_together/toggle_error.html", context)


class GameDetail(DetailView):
    model = Game


class GameCreate(CreateView):
    model = Game
    fields = ['name', 'price', 'available_on', 'multiplayer_count', 'crossplay_support', 'comment']
    success_url = reverse_lazy('play_together:player-detail')


class GameUpdate(UpdateView):
    model = Game
    fields = ['name', 'price', 'available_on', 'multiplayer_count', 'crossplay_support', 'comment']
    success_url = reverse_lazy('play_together:player-detail')


@login_required
def player_detail(request):
    player = request.user.player
    context = {
        'player': player,
        'greet': request.GET.get('greet', False) == "True",
        'add_game_form': PlayerToggleGameForm(player, is_add=True),
        'consoles': Console.objects.all()
    }
    return render(request, 'play_together/player_detail.html', context)


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


@require_http_methods(["POST"])
@login_required
def player_add_game(request):
    player = request.user.player
    form = PlayerToggleGameForm(player, request.POST, is_add=True)
    if not form.is_valid():
        return redirect(f"{reverse('play_together:toggle-error')}?next={reverse('play_together:player-detail')}")
    game = get_object_or_404(Game, pk=form.cleaned_data['toggle_game'])
    owned_game = OwnedGame(game=game, player=player)
    owned_game.save()
    player.ownedgame_set.add(owned_game)
    return HttpResponseRedirect(reverse('play_together:player-detail'))


@require_http_methods(["POST"])
@login_required
def player_remove_game(request):
    player = request.user.player
    form = PlayerToggleGameForm(player, request.POST, is_add=False)
    if not form.is_valid():
        return redirect(f"{reverse('play_together:toggle-error')}?next={reverse('play_together:player-detail')}")
    game = get_object_or_404(Game, pk=form.cleaned_data['toggle_game'])
    owned_game = OwnedGame.objects.get(game=game, player=player)
    owned_game.delete()
    return HttpResponseRedirect(reverse('play_together:player-detail'))


@login_required
def group_detail(request, pk):
    group = get_object_or_404(PlayerGroup, id=pk)
    if not request.user.player.is_part_of_group(group):
        return redirect(f"/login?next={request.path}")

    player_list = list(group.players.all())
    game_list = [
        {
            'game': game,
            'player_list': [
                [console for console in player.ownedgame_set.get(game_id=game).consoles.all()]
                    if player.ownedgame_set.filter(game_id=game).exists()
                    else False
                for player in player_list
            ]
        } for game in group.watched_games.all()
    ]
    print(game_list)
    context = {
        "group": group,
        "player_list": player_list,
        "game_list": game_list,
        "add_game_form": GroupToggleGameForm(group, is_add=True)
    }
    return render(request, "play_together/group_detail.html", context)


@require_http_methods(["POST"])
@login_required
def group_add_game(request, pk):
    group = get_object_or_404(PlayerGroup, pk=pk)
    player = request.user.player
    if not player.is_part_of_group(group):
        return redirect(f"{reverse('login')}?next={request.path}")
    form = GroupToggleGameForm(group, request.POST, is_add=True)
    if not form.is_valid():
        return redirect(f"{reverse('play_together:toggle-error')}"
                        f"?next={reverse('play_together:group-detail', args=[group.pk])}")
    game = get_object_or_404(Game, pk=form.cleaned_data['toggle_game'])
    group.watched_games.add(game)
    return HttpResponseRedirect(reverse('play_together:group-detail', args=[group.pk]))


@require_http_methods(["POST"])
@login_required
def group_remove_game(request, pk):
    group = get_object_or_404(PlayerGroup, pk=pk)
    player = request.user.player
    if not player.is_part_of_group(group):
        return redirect(f"{reverse('login')}?next={request.path}")
    form = GroupToggleGameForm(group, request.POST, is_add=False)
    if not form.is_valid():
        return redirect(f"{reverse('play_together:toggle-error')}"
                        f"?next={reverse('play_together:group-detail', args=[group.pk])}")
    game = get_object_or_404(Game, pk=form.cleaned_data['toggle_game'])
    group.watched_games.remove(game)
    return HttpResponseRedirect(reverse('play_together:group-detail', args=[group.pk]))
