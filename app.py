
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
from flask import redirect, request, session
import urllib.parse
from firebase_admin import credentials, initialize_app, auth
from spotify_api import search_tracks, get_track_lyrics
import uuid
from secret import path
load_dotenv()

# Variable Declartion
app = Flask(__name__)
cors = CORS(app, origins='*')
client_id = os.getenv("SPOTIFY_CLIENT_ID")
client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
redirect_uri = os.getenv("SPOTIFY_REDIRECT_URI")

playlists_db = {}
songs_db = {}
@app.route('/')
def index():
    return jsonify({"message": "Welcome to the Lyrics Finder API"})

cred = credentials.Certificate(path)
initialize_app(cred)

def verify_firebase_token():
    token = request.headers.get('Authorization')
    if not token:
        abort(401, description="No token provided")
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        abort(401, description=str(e))

@app.route('/login')
def login():
    scope = 'user-read-private user-read-email'
    auth_url = f"https://accounts.spotify.com/authorize?response_type=code&client_id={client_id}&scope={urllib.parse.quote(scope)}&redirect_uri={urllib.parse.quote(redirect_uri)}"
    return redirect(auth_url)

@app.route('/protected')
def protected_route():
    user = verify_firebase_token()
    return jsonify({'message': 'Protected route access granted', 'user': user})

@app.route('/callback')
def callback():
    code = request.args.get('code')
    token_url = 'https://accounts.spotify.com/api/token'
    response = requests.post(token_url, data={
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': redirect_uri,
        'client_id': client_id,
        'client_secret': client_secret
    })
    tokens = response.json()
    session['tokens'] = tokens
    return redirect('/somewhere')

def get_user_profile():
    access_token = session['tokens']['access_token']
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get('https://api.spotify.com/v1/me', headers=headers)
    return response.json()




if __name__ == '__main__':
    app.run(debug=True)
