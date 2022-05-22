import os
import sqlite3
import time
import discogs_client
from flask import Flask, render_template, request, session, redirect, url_for
from pyarr import LidarrAPI
from plexapi.server import PlexServer
from plexapi.myplex import MyPlexAccount

from db import init_db

# Config de Flask
app = Flask(__name__)
app.config.from_pyfile('config.py')
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# Config des API - services externes
LIDARR_URL = os.getenv("LIDARR_URL")
LIDARR_API = os.getenv("LIDARR_API")
DISCOGS_TOKEN = os.getenv('DISCOGS_TOKEN')
PLEX_TOKEN = os.getenv('PLEX_TOKEN')
BASE_URL_PLEX = os.getenv('BASE_URL_PLEX')
discogs = discogs_client.Client('Musicconnect/1.0', user_token=DISCOGS_TOKEN)
lidarr = LidarrAPI(LIDARR_URL, LIDARR_API)
plex = PlexServer(BASE_URL_PLEX, PLEX_TOKEN)

# Création de la DB au démarrage si inexistante
location_db = init_db.gestion_fichier_database()


# Page d'accueil de MusicLink
@app.route('/')
def index():
    if 'token' in session:
        user = MyPlexAccount(token=session['token']).username
        return render_template('index.html', username=user)
    else:
        return redirect(url_for('signin'))


@app.route('/signin', methods=['GET', 'POST'])
def signin():
    error = None
    if request.method == 'POST':
        userEmail = request.form['email']
        userPass = request.form['pass']
        usersAuthorized = plex.myPlexAccount().users()
        userAdmin = plex.myPlexAccount()
        usersAuthorizedFiltered = [user for user in usersAuthorized if user.email == userEmail]

        if not usersAuthorizedFiltered and userEmail != userAdmin.email:
            error = "Cette utilisateur ne dispose pas des droit suffisant pour accéder à ce service"
            return render_template('login.html', error=error)

        userToken = MyPlexAccount(userEmail, userPass).authenticationToken
        session['token'] = userToken
        return redirect(url_for('index'))

    return render_template('login.html', error=error)


@app.route('/signout')
def signout():
    session.clear()
    return redirect(url_for('signin'))


# Page de recherche des musiques commercial
@app.route('/search/commercial')
def recherche_commercial():
    if 'token' in session:
        return render_template('recherche_commercial.html', info="Aucun artiste recherché")
    else:
        return redirect(url_for('signin'))


# Page de recherche des musiques tekno
@app.route('/search/tekno')
def recherche_tekno():
    return render_template('recherche_tekno.html')


# Page des résultats de recherche des musiques commercial
@app.route('/result/commercial', methods=['GET'])
def resultat_commercial():
    result = request.args
    resultSearch = lidarr.lookup_artist(result['nom'])
    return render_template("recherche_commercial.html", artistsData=resultSearch)


# Page des résultats de recherche des musiques tekno
@app.route('/result/tekno', methods=['GET'])
def resultat_tekno():
    result = request.args
    n = result['nom']
    resultsSearch = discogs.search(n, type='artist')
    resultsSearch = resultsSearch[0].data
    print(resultsSearch)
    return render_template("resultat_tekno.html", artist=resultsSearch)


# Page de confirmation de l'ajout d'un artiste commercial
@app.route('/confirmed/commercial', methods=['POST'])
def confirm_commercial():
    result = request.form
    n = result['artistName']
    confirm = lidarr.add_artist(search_term=n,
                                root_dir="/music/Autres/",
                                quality_profile_id=1,
                                metadata_profile_id=1,
                                monitored=False,  # Passer a true en prod
                                artist_search_for_missing_albums=False)  # Passer a true en prod
    if "path" in confirm:
        return render_template('confirmation_commercial.html', artist=confirm)
    else:
        return render_template('erreur_commercial.html', artist=confirm)
    pass


# Page de confirmation de l'ajout d'un artiste tekno
@app.route('/confirmed/tekno', methods=['POST'])
def confirm_tekno():
    result = request.form
    conn = get_db_connection()
    sql = ''' INSERT INTO tekno(artistId, artistName, ressourceUrl, lastView) VALUES(?,?,?,?) '''
    data = (result['artistId'], result['artistName'], result['ressourceUrl'], time.time())
    conn.execute(sql, data)
    conn.commit()
    conn.close()

    # Ajout d'une "tache" prioritaire ?

    return render_template('confirmation_tekno.html', artist=result)


# Fonction de connection a la base de donnée
def get_db_connection():
    conn = sqlite3.connect(location_db)
    conn.row_factory = sqlite3.Row
    return conn


if __name__ == "__main__":
    app.run(host='0.0.0.0')
