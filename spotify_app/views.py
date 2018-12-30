from django.views.generic import TemplateView, DetailView, ListView
from django.views.generic.edit import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
# Create your views here.
from .models import Album, Playlist
from social_django.models import UserSocialAuth, USER_MODEL
import spotipy
import spotipy.util as util
from .forms import PlaylistForm
from django.http import HttpResponseRedirect
from django.shortcuts import render


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


# class PlaylistFormView(FormView):
#     template_name = 'index.html'
#     model = Playlist
#     form_class = PlaylistForm
#     success_url = '/thanks/'

def get_name(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = PlaylistForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            return HttpResponseRedirect('/')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = PlaylistForm()

    return render(request, 'index.html', {'form': form})
