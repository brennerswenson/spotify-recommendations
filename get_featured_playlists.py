from DSfunctions import *
from spotify_app.models import Playlist
from social_django.models import UserSocialAuth
import spotipy
import spotipy.util as util
from json.decoder import JSONDecodeError
import os


def main():
    scope = 'user-library-read'
    client_id = os.environ['SPOTIPY_CLIENT_ID']
    client_secret = os.environ['SPOTIPY_CLIENT_SECRET']
    redirect_uri = os.environ['SPOTIPY_REDIRECT_URI']

    # kind of dynamic way to get username, not really
    username = UserSocialAuth.objects.all().filter(id=1)[0].uid

    try:
        token = util.prompt_for_user_token(username, scope, client_id,
                                           client_secret, redirect_uri)
    except (AttributeError, JSONDecodeError):
        os.remove(f".cache-{username}")
        token = util.prompt_for_user_token(username, scope, client_id,
                                           client_secret, redirect_uri)
    sp = spotipy.Spotify(auth=token)


