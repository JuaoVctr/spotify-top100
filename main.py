from flask import Flask, redirect, request, url_for
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import logging

app = Flask(__name__)

# Configurações
CLIENT_ID = 'ef2a91da16e14ac29e7621c420b52fbf'  # Substitua pelo seu Client ID
CLIENT_SECRET = 'ca14152919c0459a8690697148872b3b' # Substitua pelo seu Client Secret
REDIRECT_URI = 'https://spotify-top100.onrender.com/callback'  # Substitua pelo seu URL no Render

# Configuração de logs
logging.basicConfig(level=logging.DEBUG)

# Autenticação
sp_oauth = SpotifyOAuth(client_id=CLIENT_ID,
                        client_secret=CLIENT_SECRET,
                        redirect_uri=REDIRECT_URI,
                        scope='user-top-read playlist-modify-public')

@app.route('/')
def index():
    try:
        auth_url = sp_oauth.get_authorize_url()
        app.logger.debug(f"URL de autorização: {auth_url}")
        return redirect(auth_url)
    except Exception as e:
        app.logger.error(f"Erro na rota /: {e}")
        return "Erro ao gerar URL de autorização. Verifique os logs.", 500

@app.route('/callback')
def callback():
    try:
        code = request.args.get('code')
        app.logger.debug(f"Código recebido: {code}")

        if not code:
            return "Erro: Código de autorização não recebido.", 400

        # Obter o token de acesso
        token_info = sp_oauth.get_access_token(code)
        app.logger.debug(f"Token info: {token_info}")

        sp = spotipy.Spotify(auth=token_info['access_token'])

        # Obter as 50 músicas mais ouvidas (limite máximo permitido)
        top_tracks = sp.current_user_top_tracks(limit=50, time_range='long_term')['items']
        track_uris = [track['uri'] for track in top_tracks]
        app.logger.debug(f"Top tracks: {track_uris}")

        # Criar a playlist
        user_id = sp.current_user()['id']
        playlist = sp.user_playlist_create(user_id, "Minhas 50 Músicas Mais Ouvidas", public=True)
        sp.playlist_add_items(playlist['id'], track_uris)
        app.logger.debug(f"Playlist criada: {playlist['external_urls']['spotify']}")

        return f"Playlist criada com sucesso! <a href='{playlist['external_urls']['spotify']}'>Acesse aqui</a>."

    except Exception as e:
        app.logger.error(f"Erro na rota /callback: {e}")
        return "Erro interno no servidor. Verifique os logs para mais detalhes.", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000, debug=False)
