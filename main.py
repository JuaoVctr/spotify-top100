from flask import Flask, redirect, request, url_for, session
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import logging
import os

app = Flask(__name__)

# Configurações
CLIENT_ID = 'ef2a91da16e14ac29e7621c420b52fbf'  # Substitua pelo seu Client ID
CLIENT_SECRET = 'ca14152919c0459a8690697148872b3b'  # Substitua pelo seu Client Secret
REDIRECT_URI = 'https://spotify-top100.onrender.com/callback'  # Substitua pelo seu URL no Render

# Chave secreta para a sessão do Flask (gerada aleatoriamente)
app.secret_key = os.urandom(24)

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
        # Gera o link de autorização e redireciona o usuário
        auth_url = sp_oauth.get_authorize_url()
        app.logger.debug(f"URL de autorização: {auth_url}")
        return redirect(auth_url)
    except Exception as e:
        app.logger.error(f"Erro na rota /: {e}")
        return "Erro ao gerar URL de autorização. Verifique os logs.", 500

@app.route('/callback')
def callback():
    try:
        # Recebe o código de autorização
        code = request.args.get('code')
        app.logger.debug(f"Código recebido: {code}")

        if not code:
            return "Erro: Código de autorização não recebido.", 400

        # Troca o código por um token de acesso
        token_info = sp_oauth.get_access_token(code)
        app.logger.debug(f"Token info: {token_info}")

        # Armazena o token de acesso na sessão do Flask
        session['token_info'] = token_info

        # Cria uma instância do Spotipy com o token do usuário
        sp = spotipy.Spotify(auth=token_info['access_token'])

        # Obtém as 50 músicas mais ouvidas do usuário
        top_tracks = sp.current_user_top_tracks(limit=50, time_range='long_term')['items']
        track_uris = [track['uri'] for track in top_tracks]
        app.logger.debug(f"Top tracks: {track_uris}")

        # Cria a playlist no perfil do usuário
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
