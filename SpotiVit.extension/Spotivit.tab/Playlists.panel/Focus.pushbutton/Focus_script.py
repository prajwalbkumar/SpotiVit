#!python3
__title__ = "Volume Up"

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

playlist_name = "AEC Flow by Bugs&Binary"


sp = Spotify(auth_manager=SpotifyOAuth(
    client_id= os.getenv("CLIENT_ID"),
    client_secret= os.getenv("CLIENT_SECRET"),
    redirect_uri="http://localhost:8888/callback",
    scope="playlist-modify-public playlist-modify-private playlist-read-private user-modify-playback-state user-read-playback-state",
    cache_path=CACHE_PATH  # Explicit cache path
))


def search_playlist(playlist_name, limit=5):
    results = sp.search(q=playlist_name, type='playlist', limit=limit)
    playlists = results.get('playlists', {}).get('items', [])

    if not playlists:
        print(f"❌ No playlists found for '{playlist_name}'.")
        return None

    for idx, playlist in enumerate(playlists, 1):
        if playlist['owner']['display_name'] == "prajwalbkumar":
            return playlist['id']
        else:
            return None


def play_playlist(playlist_id, device_id):

    playlist_uri = f"spotify:playlist:{playlist_id}"  # Convert ID to URI

    # Start playback
    sp.start_playback(device_id=device_id, context_uri=playlist_uri)



# Get available devices
devices = sp.devices()
device_list = devices["devices"]
active_device = None

for device in device_list:
    if device.get("is_active"):
        active_device = device.get("id")
        volume = int(device.get("volume_percent"))
        break

else:
    print("❌ No active devices found. Open Spotify on a device.")

playlist_id = search_playlist(playlist_name)

if active_device:
    play_playlist(playlist_id, active_device)