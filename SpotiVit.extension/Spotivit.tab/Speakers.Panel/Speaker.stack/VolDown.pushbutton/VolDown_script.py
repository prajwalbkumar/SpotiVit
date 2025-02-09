#!python3
__title__ = "Volume Down"

import sys
sys.path.append(r'C:\Users\arpra\AppData\Local\Programs\Python\Python38\Lib\site-packages')

import os
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

current_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.abspath(os.path.join(current_dir, '..', '..', '..','..', '.env'))
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


# Select the first available device
if active_device:
    volume = volume - 5    
    if volume < 0:
        volume = 0

    sp.volume(volume_percent=volume)