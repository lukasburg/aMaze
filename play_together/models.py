from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.urls import reverse

from django.db.models.signals import post_save
from django.dispatch import receiver
from pprint import pprint


class Console(models.Model):
    name = models.CharField(max_length=50, unique=True)
    icon = models.ImageField(null=True, upload_to="console-icon/")

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


class OwnedGames(models.Model):
    player = models.ForeignKey("Player", on_delete=models.CASCADE)
    console = models.ForeignKey(Console, on_delete=models.PROTECT)
    game = models.ForeignKey(Game, on_delete=models.PROTECT)

    def clean(self):
        pprint(self.game.available_on.all())
        if not self.game.available_on.filter(id=self.console.id).exists():
            raise ValidationError(f"{self.game} seems to not exist on {self.console}.")

    class Meta:
        verbose_name = 'Owned Game'
        verbose_name_plural = 'Owned Games Plural'


# Players
class Player(models.Model):
    # Reference backend user:
    # https://docs.djangoproject.com/en/3.1/topics/auth/customizing/#extending-the-existing-user-model
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    my_games = models.ManyToManyField(Game, through=OwnedGames)
    my_consoles = models.ManyToManyField(Console, blank=True)

    def is_part_of_group(self, group):
        return self.playergroup_set.filter(id=group.id).exists()

    def __str__(self):
        return self.user.username

    def get_absolute_url(self):
        return reverse('play_together:profile')


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
        return reverse('play_together:group_view', args=[self.id])

    class Meta:
        verbose_name = 'Player Group'
        verbose_name_plural = 'Player Groups'
