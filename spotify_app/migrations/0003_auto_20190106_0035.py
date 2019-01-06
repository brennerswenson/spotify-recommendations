# Generated by Django 2.1.4 on 2019-01-06 00:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('spotify_app', '0002_auto_20190106_0032'),
    ]

    operations = [
        migrations.AlterField(
            model_name='song',
            name='parent_playlist',
            field=models.ForeignKey(db_column='parent_playlist_id', on_delete=django.db.models.deletion.CASCADE, to='spotify_app.Playlist'),
        ),
    ]