from collections import Counter

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.decorators.http import require_http_methods
from django.views.generic.detail import DetailView
from django_http_exceptions import HTTPExceptions

from .decorators import login_required_return_denied
from .forms import PlayerToggleGameForm, GroupToggleGameForm, GameCreateUpdateForm, CreateWithRedirectView, \
    UpdateWithRedirectView
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


class GameCreate(LoginRequiredMixin, CreateWithRedirectView):
    model = Game
    form_class = GameCreateUpdateForm
    success_url = reverse_lazy('play_together:player-detail')

    def form_valid(self, form):
        response = super().form_valid(form)
        player = self.request.user.player
        if form.cleaned_data['add_to_your_games']:
            player.games.add(form.instance)
        return response


class GameUpdate(LoginRequiredMixin, UpdateWithRedirectView):
    model = Game
    form_class = GameCreateUpdateForm
    success_url = reverse_lazy('play_together:player-detail')

    def form_valid(self, form):
        response = super().form_valid(form)
        player = self.request.user.player
        if form.cleaned_data['add_to_your_games']:
            player.games.add(form.instance)
        return response


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


def number_can_play_together(game, player_console_list):
    if game.crossplay_support == 'full':
        return None, len(player_console_list) - player_console_list.count(False)
    grouped = Counter(console for player_list in player_console_list if player_list for console in player_list)
    return grouped.most_common(1)[0]


def number_could_play_together(game, player_list):
    if game.crossplay_support == 'full':
        score = 0
        for player in player_list:
            if player.consoles.filter(id__in=game.available_on.all()).exists():
                score = score + 1
        return None, score
    grouped = Counter()
    for player in player_list:
        grouped.update(player.consoles.filter(id__in=game.available_on.all()).all())
    return grouped.most_common(1)[0]


@login_required
def group_detail(request, pk):
    order = request.GET.get('order', 'can_play')
    group = get_object_or_404(PlayerGroup, id=pk)
    if not request.user.player.is_part_of_group(group):
        return redirect(f"/login?next={request.path}")

    player_list = group.players.order_by()
    annotated_game_list = [
        {
            'game': game,
            'player_console_list': [player.get_consoles_for_game(game) for player in player_list]
        } for game in group.watched_games.all()
    ]
    for annotated_game in annotated_game_list:
        game = annotated_game['game']
        annotated_game['can_play'] = number_can_play_together(game, annotated_game['player_console_list'])
        annotated_game['could_play'] = number_could_play_together(game, player_list)

    def crossplay_score(it):
        return it['game'].crossplay_support == 'full'

    ordered_list = sorted(annotated_game_list, key=crossplay_score, reverse=True)
    print(ordered_list)
    ordered_list = sorted(ordered_list, key=lambda an: an['could_play'][1], reverse=True)
    ordered_list = sorted(ordered_list, key=lambda an: an['can_play'][1], reverse=True)
    context = {
        "group": group,
        "player_list": player_list,
        "game_list": ordered_list,
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
