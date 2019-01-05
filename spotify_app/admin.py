from django.contrib import admin
from spotify_app.models import Playlist, Song


# Register your models here.

# class RatingAdmin(admin.ModelAdmin):
#     readonly_fields = ('date_added',)
#
#
# admin.site.register(Playlist, RatingAdmin)
# admin.site.register(Song, RatingAdmin)

admin.site.register(Playlist)
admin.site.register(Song)
