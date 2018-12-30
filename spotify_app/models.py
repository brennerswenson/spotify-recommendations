from django.db import models


# Create your models here.


class Artist(models.Model):
    artist_id = models.CharField(max_length=500, primary_key=True)


class Album(models.Model):
    album_id = models.CharField(max_length=500)
    album_name = models.CharField(max_length=500)
    release_date = models.DateTimeField()
    album_popularity = models.CharField(max_length=50)
    album_explicit = models.BooleanField(null=False)


class Song(models.Model):
    song_id = models.CharField(max_length=120, primary_key=True)
    song_name = models.TextField(blank=False, null=False)
    artist_name = models.CharField(max_length=120, blank=False, null=False)
    artist_id = models.ForeignKey(Artist, on_delete=models.CASCADE)
    album_id = models.ForeignKey(Album, on_delete=models.CASCADE)


class Playlist(models.Model):
    playlist_id = models.CharField(max_length=120, primary_key=True)
    playlist_name = models.TextField(blank=False, null=False)
    playlist_url = models.CharField(max_length=1000, blank=False, null=False)
    playlist_num_tracks = models.IntegerField()


