
from flask import Flask, request, jsonify
from firebase_admin import credentials, initialize_app, auth
from spotify_api import search_tracks, get_track_lyrics
import uuid
from secret import path

app = Flask(__name__)


cred = credentials.Certificate(path)
initialize_app(cred)


playlists_db = {}
songs_db = {}
@app.route('/')
def landing_page():
    return {
        "Movies from these three GENRES" : "1:Superheros,2:Wild-West,3:Monsterverse,4:Supernatral,5:Paranormal,5:Romcom,6:Holidays"
    }

@app.route('/api/search', methods=['GET'])
def search():
    query = request.args.get('query')
    if not query:
        return jsonify({'error': 'Missing query parameter'}), 400

    tracks = search_tracks(query)
    if not tracks:
        return jsonify({'error': 'No tracks found'}), 404

    # Cache songs for easier access later
    for track in tracks:
        songs_db[track['id']] = track

    return jsonify({'tracks': tracks})

@app.route('/api/lyrics/<track_id>', methods=['GET'])
def lyrics(track_id):
    lyrics = get_track_lyrics(track_id)
    return jsonify({'lyrics': lyrics})

@app.route('/api/playlists', methods=['GET', 'POST'])
def playlists():
    if request.method == 'POST':
        data = request.json
        new_playlist_id = str(uuid.uuid4())
        new_playlist = {
            'id': new_playlist_id,
            'user_id': data['user_id'],
            'name': data['name'],
            'songs': []
        }
        playlists_db[new_playlist_id] = new_playlist
        return jsonify(new_playlist), 201

    user_id = request.args.get('user_id')
    if user_id:
        user_playlists = [playlist for playlist in playlists_db.values() if playlist['user_id'] == user_id]
        return jsonify(user_playlists)

    return jsonify([])

@app.route('/api/playlists/<playlist_id>', methods=['PUT', 'DELETE'])
def update_playlist(playlist_id):
    playlist = playlists_db.get(playlist_id)
    if not playlist:
        return jsonify({'error': 'Playlist not found'}), 404

    if request.method == 'PUT':
        data = request.json
        if 'name' in data:
            playlist['name'] = data['name']
        if 'songs' in data:
            playlist['songs'] = data['songs']
        playlists_db[playlist_id] = playlist
        return jsonify(playlist)

    if request.method == 'DELETE':
        del playlists_db[playlist_id]
        return '', 204

    return jsonify({})

@app.route('/api/playlists/<playlist_id>/songs', methods=['POST', 'DELETE'])
def update_playlist_songs(playlist_id):
    playlist = playlists_db.get(playlist_id)
    if not playlist:
        return jsonify({'error': 'Playlist not found'}), 404

    if request.method == 'POST':
        data = request.json
        song_id = data.get('song_id')
        if not song_id or song_id not in songs_db:
            return jsonify({'error': 'Invalid song ID'}), 400

        if song_id not in playlist['songs']:
            playlist['songs'].append(song_id)
        playlists_db[playlist_id] = playlist
        return jsonify(playlist)

    if request.method == 'DELETE':
        data = request.json
        song_id = data.get('song_id')
        if not song_id or song_id not in playlist['songs']:
            return jsonify({'error': 'Invalid song ID'}), 400

        playlist['songs'].remove(song_id)
        playlists_db[playlist_id] = playlist
        return jsonify(playlist)

if __name__ == '__main__':
    app.run(debug=True)
