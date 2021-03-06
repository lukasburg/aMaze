from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.urls import reverse

from django.db.models.signals import post_save
from django.dispatch import receiver


class Console(models.Model):
    name = models.CharField(max_length=50, unique=True)
    icon = models.ImageField(upload_to="console-icon/")

    def __str__(self):
        return self.name


class Game(models.Model):
    name = models.CharField(max_length=50, unique=True)
    price = models.PositiveIntegerField(help_text="Approximate Price on any Source")
    available_on = models.ManyToManyField(Console)
    multiplayer_count = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    FULL = "full"
    PARTIALLY = "part"
    NONE = "none"
    CROSSPLAY_CHOICES = [
        (FULL, "Full Support"),
        (PARTIALLY, "Partial Support (See below)"),
        (NONE, "No Support"),
    ]
    crossplay_support = models.CharField(max_length=4, choices=CROSSPLAY_CHOICES)
    comment = models.TextField(
        max_length=2000, help_text="Specify crossplay conditions or any other info", blank=True
    )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('play_together:game-detail', kwargs={'pk': self.pk})


class OwnedGame(models.Model):
    player = models.ForeignKey("Player", on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.PROTECT)
    consoles = models.ManyToManyField(Console, blank=True)

    def clean(self):
        for console in self.consoles.all():
            if not self.game.available_on.filter(id=console).exists():
                raise ValidationError(f"{self.game} seems to not exist on {self.console}.")
            if not self.player.consoles.filter(id=console).exists():
                raise ValidationError(f"You don't seem to own {self.console}.")

    class Meta:
        verbose_name = 'Owned Game'
        verbose_name_plural = 'Owned Games Plural'


# Players
class Player(models.Model):
    # Reference backend user:
    # https://docs.djangoproject.com/en/3.1/topics/auth/customizing/#extending-the-existing-user-model
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    games = models.ManyToManyField(Game, verbose_name="Your Games", through=OwnedGame, blank=True)
    consoles = models.ManyToManyField(Console, verbose_name="Your Consoles", blank=True)

    def is_part_of_group(self, group):
        return self.playergroup_set.filter(id=group.id).exists()

    def __str__(self):
        return self.user.username

    def get_consoles_for_game(self, game):
        if self.ownedgame_set.filter(game_id=game).exists():
            return [console for console in self.ownedgame_set.get(game_id=game).consoles.all()]
        else:
            return False

    def get_absolute_url(self):
        return reverse('play_together:player-detail')


@receiver(post_save, sender=User)
def create_player_for_user(sender, created, instance, **kwargs):
    if created:
        connected_player = Player(user=instance)
        connected_player.save()


class PlayerGroup(models.Model):
    name = models.CharField(max_length=50)
    players = models.ManyToManyField(Player)
    watched_games = models.ManyToManyField(Game, blank=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('group-detail', args=[self.id])

    class Meta:
        verbose_name = 'Player Group'
        verbose_name_plural = 'Player Groups'
