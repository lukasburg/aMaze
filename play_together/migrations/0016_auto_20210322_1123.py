# Generated by Django 3.1.7 on 2021-03-22 11:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('play_together', '0015_auto_20210322_1122'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='OwnedGames',
            new_name='OwnedGame',
        ),
    ]
