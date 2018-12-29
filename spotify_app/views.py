from django.shortcuts import render
from django.views.generic import TemplateView
import datetime
# Create your views here.
from .models import Album

class AlbumDetailView(TemplateView):
    template_name = 'spotify_app/album_detail.html'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['albums'] = Album.objects.all()
        return context



