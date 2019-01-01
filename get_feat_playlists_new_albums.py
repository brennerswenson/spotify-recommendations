import os, django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "spotify_recs.settings")
django.setup()
from social_django.models import UserSocialAuth
from spotify_app.models import Playlist
import spotipy
import spotipy.util as util
from json.decoder import JSONDecodeError
from DSfunctions import *


def main():
    scope = 'user-library-read'
    client_id = os.environ['SPOTIPY_CLIENT_ID']
    client_secret = os.environ['SPOTIPY_CLIENT_SECRET']
    redirect_uri = os.environ['SPOTIPY_REDIRECT_URI']

    try:
        # kind of dynamic way to get username, not really
        username = UserSocialAuth.objects.all().filter(id=1)[0].uid
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

    payload = sp.featured_playlists()['playlists']

    playlist_total = payload['items']

    while payload['next']:
        payload = sp.next(payload)
        playlist_total.extend(payload['items'])

    print('Getting featured playlists...')

    for playlist in playlist_total:
        temp_obj = Playlist(playlist_id=playlist['id'],
                            playlist_name=playlist['name'],
                            playlist_url=playlist['external_urls']['spotify'],
                            playlist_num_tracks=playlist['tracks']['total'],
                            playlist_featured=True)
        temp_obj.save()


if __name__ == '__main__':
    main()
