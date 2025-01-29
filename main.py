from flask import Flask, redirect, request, url_for
import spotipy
from spotipy.oauth2 import SpotifyOAuth

app = Flask(__name__)

# Configurações
CLIENT_ID = 'ef2a91da16e14ac29e7621c420b52fbf'  # Substitua pelo seu Client ID
CLIENT_SECRET = 'ca14152919c0459a8690697148872b3b'  # Substitua pelo seu Client Secret
REDIRECT_URI = 'https://spotify-top100.onrender.com'  # Altere para o URL do Render

# Autenticação
sp_oauth = SpotifyOAuth(client_id=CLIENT_ID,
                        client_secret=CLIENT_SECRET,
                        redirect_uri=REDIRECT_URI,
                        scope='user-top-read playlist-modify-public')

@app.route('/')
def index():
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    sp = spotipy.Spotify(auth=token_info['access_token'])

    # Obter as 100 músicas mais ouvidas
    top_tracks = sp.current_user_top_tracks(limit=100, time_range='long_term')['items']
    track_uris = [track['uri'] for track in top_tracks]

    # Criar a playlist
    user_id = sp.current_user()['id']
    playlist = sp.user_playlist_create(user_id, "Minhas 100 Músicas Mais Ouvidas", public=True)
    sp.playlist_add_items(playlist['id'], track_uris)

    return f"Playlist criada com sucesso! <a href='{playlist['external_urls']['spotify']}'>Acesse aqui</a>."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
