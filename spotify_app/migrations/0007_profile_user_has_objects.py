# Generated by Django 2.1.4 on 2019-01-13 19:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spotify_app', '0006_auto_20190113_1902'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='user_has_objects',
            field=models.BooleanField(default=False, null=True),
        ),
    ]
