from django.contrib import admin
from spotify_app.models import Album, Playlist

# Register your models here.
admin.site.register(Playlist)
admin.site.register(Album)