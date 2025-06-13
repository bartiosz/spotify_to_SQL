from flask import Flask, request, redirect
import requests
import base64
import urllib.parse
import os
from dotenv import set_key, load_dotenv
from pathlib import Path

# Spotify app credentials
load_dotenv()
CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
REDIRECT_URI = os.getenv('SPOTIFY_REDIRECT_URI')

# Check for .env file
env_path = Path('.') / '.env'

app = Flask(__name__)

@app.route('/')
def login():
    scope = 'user-library-read'
    auth_url = 'https://accounts.spotify.com/authorize'
    query_params = {
        'client_id': CLIENT_ID,
        'response_type': 'code',
        'redirect_uri': REDIRECT_URI,
        'scope': scope
    }
    url = f'{auth_url}?{urllib.parse.urlencode(query_params)}'
    return redirect(url)

@app.route('/callback')
def callback():
    code = request.args.get('code')

    token_url = 'https://accounts.spotify.com/api/token'
    auth_header = base64.b64encode(f'{CLIENT_ID}:{CLIENT_SECRET}'.encode()).decode()

    payload = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI
    }

    headers = {
        'Authorization': f'Basic {auth_header}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    response = requests.post(token_url, data=payload, headers=headers)
    tokens = response.json()

    access_token = tokens.get('access_token')
    refresh_token = tokens.get('refresh_token')

    # Save tokens to .env
    set_key(str(env_path), 'SPOTIFY_ACCESS_TOKEN', access_token)
    set_key(str(env_path), 'SPOTIFY_REFRESH_TOKEN', refresh_token)

    return f'Access Token: {access_token}<br>Refresh Token: {refresh_token}'

if __name__ == '__main__':
    app.run(port=8888)
