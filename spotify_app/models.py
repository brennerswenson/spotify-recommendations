from django.db import models


class Song(models.Model):
    class Meta:
        app_label = 'spotify_app'

    song_id = models.CharField(max_length=120, primary_key=True)
    song_name = models.TextField(blank=False, null=False)
    artist_name = models.CharField(max_length=120, blank=False, null=False)
    song_is_explicit = models.BooleanField(blank=False)
    song_popularity = models.DecimalField(max_digits=1000, decimal_places=2)
    song_duration_ms = models.IntegerField(blank=False)
    recommended_user = models.CharField(blank=False, max_length=500)
    date_created = models.CharField(max_length=500, default='No date')

    def __str__(self):
        return self.song_name


class Playlist(models.Model):
    class Meta:
        app_label = 'spotify_app'

    playlist_id = models.CharField(max_length=120, primary_key=True)
    playlist_name = models.TextField(max_length=100)
    playlist_url = models.CharField(max_length=1000)
    playlist_num_tracks = models.IntegerField(null=True)
    playlist_featured = models.BooleanField(default=False)
    playlist_owner = models.CharField(max_length=500)
    date_created = models.CharField(max_length=500, default='No date')

    def __str__(self):
        return self.playlist_name
