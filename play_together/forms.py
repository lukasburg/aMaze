from django import forms
from .models import Game
from django.views.generic.edit import FormMixin, CreateView, UpdateView


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


class GameCreateUpdateForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = '__all__'
        widgets = {
            'available_on': forms.CheckboxSelectMultiple
        }

    add_to_your_games = forms.BooleanField(initial=False, required=False)


class BaseRedirectMixin(FormMixin):
    def get_initial(self):
        initial = self.initial.copy()
        initial['success_redirect'] = self.request.GET.get('success_redirect')
        return initial

    def get_form(self, form_class=None):
        form = super().get_form()
        form.fields['success_redirect'] = forms.CharField(max_length=100, widget=forms.HiddenInput, required=False)
        return form

    def form_valid(self, form):
        self.success_url = form.cleaned_data['success_redirect']
        return super().form_valid(form)


class CreateWithRedirectView(BaseRedirectMixin, CreateView):
    pass


class UpdateWithRedirectView(BaseRedirectMixin, UpdateView):
    pass
