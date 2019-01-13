# Generated by Django 2.1.4 on 2019-01-13 17:45

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('spotify_app', '0002_auto_20190113_1729'),
    ]

    operations = [
        migrations.RenameField(
            model_name='profile',
            old_name='kmeans_object',
            new_name='user_kmeans',
        ),
        migrations.RemoveField(
            model_name='song',
            name='album_cover_art',
        ),
        migrations.AlterField(
            model_name='profile',
            name='user',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]