#!python3
__title__ = "Authenticate"

import sys
sys.path.append(r'C:\Users\arpra\AppData\Local\Programs\Python\Python38\Lib\site-packages')

import os
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

current_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.abspath(os.path.join(current_dir, '..', '..', '..', '.env'))
load_dotenv(env_path)

# Set a stable cache path
CACHE_PATH = os.path.join(os.getenv('APPDATA'), 'SpotiVit', '.cache')
os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)

sp = Spotify(auth_manager=SpotifyOAuth(
    client_id= os.getenv("CLIENT_ID"),
    client_secret= os.getenv("CLIENT_SECRET"),
    redirect_uri="http://localhost:8888/callback",
    scope="user-read-playback-state user-read-currently-playing user-modify-playback-state",
    cache_path=CACHE_PATH  # Explicit cache path
))