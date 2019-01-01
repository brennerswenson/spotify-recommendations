from django.views.generic import TemplateView, DetailView, ListView
from django.views.generic.edit import FormView, FormMixin
from django.contrib.auth.mixins import LoginRequiredMixin
# Create your views here.
from .models import Album, Playlist, Song
import spotipy
import spotipy.util as util
from .forms import PlaylistInputForm

from django.contrib.auth import get_user_model
from social_django.models import UserSocialAuth
from django.urls import reverse_lazy
import os
from json.decoder import JSONDecodeError
import get_feat_playlists_new_albums
from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import redirect

import ds_pipeline as ds

User = get_user_model()


class PlaylistListFormView(LoginRequiredMixin, ListView, FormView, FormMixin):
    get_feat_playlists_new_albums.main()  # get featured playlists on launch

    model = Playlist
    template_name = 'index.html'
    queryset = Playlist.objects.all()
    form_class = PlaylistInputForm
    success_url = reverse_lazy('spotify_app:playlist_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['playlists'] = Playlist.objects.all()
        context['form'] = self.get_form()
        return context

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            print(dir(request))
            instance = form.save(commit=False)
            instance.playlist_id = instance.playlist_id.split(':')[4]  # filter down to the playlist ID
            scope = 'user-library-read'
            client_id = os.environ['SPOTIPY_CLIENT_ID']
            client_secret = os.environ['SPOTIPY_CLIENT_SECRET']
            redirect_uri = os.environ['SPOTIPY_REDIRECT_URI']

            rec_id = request.user.id

            # get spotify username based on admin userID
            # don't know if this is going to work with someone other than myself
            try:
                username = UserSocialAuth.objects.all().filter(id=rec_id)[0].uid
            except IndexError:
                username = 'brennerswenson'

            try:
                token = util.prompt_for_user_token(username, scope, client_id,
                                                   client_secret, redirect_uri)
            except (AttributeError, JSONDecodeError):
                os.remove(f".cache-{username}")
                token = util.prompt_for_user_token(username, scope, client_id,
                                                   client_secret, redirect_uri)

            sp = spotipy.Spotify(auth=token)

            playlist = sp.user_playlist(username, playlist_id=instance.playlist_id)
            instance.playlist_name = playlist['name']
            print(instance.playlist_name)
            instance.playlist_url = playlist['external_urls']['spotify']
            print(instance.playlist_url)
            instance.playlist_num_tracks = len(playlist['tracks']['items'])
            instance.playlist_owner = playlist['owner']['display_name']
            instance.save()
            return redirect('spotify_app:playlist_detail', playlist_id=instance.playlist_id)
        else:
            return self.form_invalid(form)


# FINISH THIS LATER! FIGURE OUT HOW TO STORE RECOMMENDED SONGS IN DB AND LIST THEM OUT
class ChosenPlaylistListView(ListView):
    template_name = 'recommendations.html'
    model = Playlist
    playlist_id = None

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['chosen_playlist'] = Playlist.objects.get(playlist_id=self.kwargs['playlist_id'])

        return context
