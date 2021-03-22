from django import forms
from .models import Game


class PlayerToggleGameForm(forms.Form):
    toggle_game = forms.ChoiceField()

    def __init__(self, player, *args, is_add=True, **kwargs):
        super().__init__(*args, **kwargs)
        if is_add:
            add_games = Game.objects.exclude(
                id__in=player.games.values_list('id')
            ).values_list('id', 'name')
            self.fields['toggle_game'].choices = add_games
        else:
            remove_games = Game.objects.filter(
                id__in=player.games.values_list('id')
            ).values_list('id', 'name')
            self.fields['toggle_game'].choices = remove_games


class GroupToggleGameForm(forms.Form):
    toggle_game = forms.ChoiceField()

    def __init__(self, group, *args, is_add=True, **kwargs):
        super().__init__(*args, **kwargs)
        if is_add:
            add_games = Game.objects.exclude(
                id__in=group.watched_games.values_list('id')
            ).values_list('id', 'name')
            self.fields['toggle_game'].choices = add_games
        else:
            remove_games = Game.objects.filter(
                id__in=group.watched_games.values_list('id')
            ).values_list('id', 'name')
            self.fields['toggle_game'].choices = remove_games

