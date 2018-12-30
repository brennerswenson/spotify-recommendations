from django.views.generic import TemplateView, DetailView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
# Create your views here.
from .models import Album, Playlist
from social_django.models import UserSocialAuth, USER_MODEL
import spotipy
import spotipy.util as util


class HomeTemplateView(TemplateView):
    template_name = 'index.html'


class PlaylistListView(LoginRequiredMixin, ListView):
    model = Playlist
    template_name = 'index.html'
    queryset = Playlist.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['playlists'] = Playlist.objects.all()
        return context
