import os
import sqlite3
import time
import discogs_client
import downloader
from celery import Celery
from flask import Flask, render_template, request, session, redirect, url_for
from pyarr import LidarrAPI
from plexapi.server import PlexServer

from db.init_db import create_db

from plexOauth import oauth

# Config de Flask + Celery
app = Flask(__name__)
app.config.from_pyfile('config.py')
app.config['CELERY_BROKER_URL'] = os.getenv("CELERY_BROKER_URL")
app.config['CELERY_RESULT_BACKEND'] = os.getenv("CELERY_RESULT_BACKEND")
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.config.from_pyfile('config.py')
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])

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
create_db()


# Page d'accueil de MusicLink
@app.route('/')
def index():
    if 'token' in session:
        return render_template('index.html')
    else:
        return redirect(url_for('signin'))


@app.route('/signin')
def signin():
    if 'token' in session:
        return redirect(url_for('index'))
    return render_template('no_auth.html')


@app.route('/signout')
def signout():
    session.clear()
    return redirect(url_for('signin'))


@app.route('/plex/oauth', methods=['POST'])
async def plex_oauth():
    token = await oauth()
    session['token'] = token

    if token:
        return redirect(url_for('index'))

    return redirect(url_for('signin'))


# Page de recherche des musiques commercial
@app.route('/search/commercial')
def recherche_commercial():
    if 'token' in session:
        return render_template('recherche_commercial.html', info="Pas d'artist rechercher")
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

    analyseTekno.delay(result['artistId'])

    return render_template('confirmation_tekno.html', artist=result)


# Fonction de connection a la base de donnée
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


@celery.task
def analyseTekno(artistId):
    print("Analyse et téléchargements")
    downloader.get_tracks(artistId)


if __name__ == "__main__":
    app.run()
