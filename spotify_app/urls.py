from django.contrib import admin
from django.urls import path, include
from . import views

app_name = 'spotify_app'

urlpatterns = [
    path('playlists/', views.PlaylistListView.as_view(), name='playlist_list'),
    path('playlists/', views.get_name, name='get_name'),
]