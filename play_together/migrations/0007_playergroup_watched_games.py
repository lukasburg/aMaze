# Generated by Django 3.1.7 on 2021-03-20 11:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("play_together", "0006_playergroup"),
    ]

    operations = [
        migrations.AddField(
            model_name="playergroup",
            name="watched_games",
            field=models.ManyToManyField(to="play_together.Game"),
        ),
    ]
