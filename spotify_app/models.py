from django.db import models


class Artist(models.Model):
    artist_id = models.CharField(max_length=500, primary_key=True)
    artist_followers = models.IntegerField()


class Album(models.Model):
    album_id = models.CharField(max_length=500, primary_key=True)
    album_name = models.CharField(max_length=500)
    release_date = models.DateTimeField()
    album_popularity = models.CharField(max_length=50)
    album_explicit = models.BooleanField(null=False)
    album_release_date = models.CharField(max_length=100, blank=False)

    def __str__(self):
        return self.album_name


class Song(models.Model):
    song_id = models.CharField(max_length=120, primary_key=True)
    song_name = models.TextField(blank=False, null=False)
    artist_name = models.CharField(max_length=120, blank=False, null=False)
    album_id = models.ForeignKey(Album, on_delete=models.CASCADE)
    artist_id = models.ForeignKey(Artist, on_delete=models.CASCADE)
    song_is_explicit = models.BooleanField(blank=False)
    song_popularity = models.DecimalField(max_digits=1000, decimal_places=2)
    song_duration_ms = models.IntegerField(blank=False)

    def __str__(self):
        return self.song_name


class Playlist(models.Model):
    playlist_id = models.CharField(max_length=120, primary_key=True)
    playlist_name = models.TextField(max_length=100)
    playlist_url = models.CharField(max_length=1000)
    playlist_num_tracks = models.IntegerField(null=True)
    playlist_featured = models.BooleanField(default=False)
    playlist_owner = models.CharField(max_length=500)

    def __str__(self):
        return self.playlist_name
