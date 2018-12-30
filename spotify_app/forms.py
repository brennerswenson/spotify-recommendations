from django import forms
from .models import Playlist


class PlaylistForm(forms.Form):
    playlist_id = forms.CharField(label='Spotify Playlist URI', max_length=500)

    def clean_id(self):
        data = self.cleaned_data['playlist_id']
        return data
