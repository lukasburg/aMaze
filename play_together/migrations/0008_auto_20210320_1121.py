# Generated by Django 3.1.7 on 2021-03-20 11:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("play_together", "0007_playergroup_watched_games"),
    ]

    operations = [
        migrations.AlterField(
            model_name="playergroup",
            name="watched_games",
            field=models.ManyToManyField(null=True, to="play_together.Game"),
        ),
    ]
