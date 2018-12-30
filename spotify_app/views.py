from django.views.generic import TemplateView, DetailView, ListView
from django.views.generic.edit import FormView, FormMixin
from django.contrib.auth.mixins import LoginRequiredMixin
# Create your views here.
from .models import Album, Playlist
import spotipy
import spotipy.util as util
from .forms import PlaylistForm

from django.contrib.auth import get_user_model
from social_django.models import UserSocialAuth
from django.urls import reverse_lazy
import os
from json.decoder import JSONDecodeError

User = get_user_model()


class HomeTemplateView(TemplateView):
    template_name = 'index.html'


class PlaylistListFormView(LoginRequiredMixin, ListView, FormView, FormMixin):
    model = Playlist
    template_name = 'index.html'
    queryset = Playlist.objects.all()
    form_class = PlaylistForm
    success_url = reverse_lazy('spotify_app:playlist_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['playlists'] = Playlist.objects.all()
        context['form'] = self.get_form()
        return context

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():

            instance = form.save(commit=False)
            instance.playlist_id = instance.playlist_id.split(':')[4]  # filter down to the playlist ID
            scope = 'user-library-read'
            client_id = os.environ['SPOTIPY_CLIENT_ID']
            client_secret = os.environ['SPOTIPY_CLIENT_SECRET']
            redirect_uri = os.environ['SPOTIPY_REDIRECT_URI']

            rec_id = request.user.id

            # get spotify username based on admin userID
            # don't know if this is going to work with someone other than myself
            username = UserSocialAuth.objects.all().filter(id=rec_id)[0].uid

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
            instance.save()
            return self.form_valid(form)
        else:
            return self.form_invalid(form)
