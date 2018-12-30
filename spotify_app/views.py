from django.views.generic import TemplateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
# Create your views here.
from .models import Album



class HomeTemplateView(TemplateView):
    template_name = 'index.html'



class AlbumDetailView(LoginRequiredMixin, DetailView):
    template_name = 'spotify_app/album_detail.html'

    def get_context_data(self, **kwargs):
        queryset = super().get_context_data(**kwargs)
        queryset['albums'] = Album.objects.all()
        return queryset
