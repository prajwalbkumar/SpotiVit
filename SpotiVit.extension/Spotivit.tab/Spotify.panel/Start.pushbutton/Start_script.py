#!python3
__title__ = "Spotify for Revit"

import sys
sys.path.append(r'C:\Users\arpra\AppData\Local\Programs\Python\Python38\Lib\site-packages')

import os
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth

# Set a stable cache path
CACHE_PATH = os.path.join(os.getenv('APPDATA'), 'SpotifyForRevit', '.cache')
os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)

sp = Spotify(auth_manager=SpotifyOAuth(
    client_id="0da0085552cb41029dbba572d0b4724a",
    client_secret="2b69fa98730843d4aa7b4ffe13ad387e",
    redirect_uri="http://localhost:8888/callback",
    scope="user-modify-playback-state user-read-playback-state user-read-currently-playing",
    cache_path=CACHE_PATH  # Explicit cache path
))

devices = sp.devices()
# sp.shuffle(True)
# sp.pause_playback()

sp.start_playback()