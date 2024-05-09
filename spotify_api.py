from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
from secret import spotify_Client_id,spotify_CS

SPOTIFY_CLIENT_ID = spotify_Client_id
SPOTIFY_CLIENT_SECRET = spotify_CS

credentials_manager = SpotifyClientCredentials(
    client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET
)
spotify = Spotify(client_credentials_manager=credentials_manager)

def search_tracks(query):
    results = spotify.search(q=query, type='track', limit=10)
    tracks = results['tracks']['items']
    return [
        {
            'id': track['id'],
            'name': track['name'],
            'artists': ', '.join([artist['name'] for artist in track['artists']]),
            'album': track['album']['name'],
            'preview_url': track['preview_url'],
            'external_url': track['external_urls']['spotify']
        }
        for track in tracks
    ]

def get_track_lyrics(track_id):
    # Example: Here, you can integrate a lyrics service like Genius, etc.
    # For demonstration, returning static lyrics
    return "Lyrics for the song will go here."

