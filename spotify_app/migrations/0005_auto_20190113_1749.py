# Generated by Django 2.1.4 on 2019-01-13 17:49

from django.db import migrations
import picklefield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('spotify_app', '0004_song_album_cover_art'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='user_kmeans',
            field=picklefield.fields.PickledObjectField(default='no_object_yet', editable=False, null=True),
        ),
    ]