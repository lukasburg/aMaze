# Generated by Django 3.1.7 on 2021-03-19 19:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("play_together", "0002_auto_20210319_1929"),
    ]

    operations = [
        migrations.RenameField(
            model_name="player",
            old_name="backend_user",
            new_name="user",
        ),
    ]
