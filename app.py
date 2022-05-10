import os
import sqlite3
import time

import discogs_client
from flask import Flask, render_template, request, flash
from pyarr import LidarrAPI

from db.init_db import create_db

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.config.from_pyfile('config.py')

LIDARR_URL = os.getenv("LIDARR_URL")
LIDARR_API = os.getenv("LIDARR_API")
DISCOGS_TOKEN = os.getenv('DISCOGS_TOKEN')

discogs = discogs_client.Client('Musicconnect/1.0', user_token=DISCOGS_TOKEN)
lidarr = LidarrAPI(LIDARR_URL, LIDARR_API)

create_db()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/searchcommercial')
def recherche_commercial():
    return render_template('recherche_commercial.html')


@app.route('/searchtekno')
def recherche_tekno():
    return render_template('recherche_tekno.html')


@app.route('/resultcommercial', methods=['GET'])
def resultat_commercial():
    result = request.args
    resultSearch = lidarr.lookup_artist(result['nom'])
    return render_template("recherche_commercial.html", artistsData=resultSearch)


@app.route('/resulttekno', methods=['GET'])
def resultat_tekno():
    result = request.args
    n = result['nom']
    resultsSearch = discogs.search(n, type='artist')
    resultsSearch = resultsSearch[0].data
    print(resultsSearch)
    return render_template("resultat_tekno.html", artist=resultsSearch)


@app.route('/confirmedcommercial', methods=['POST'])
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


@app.route('/confirmedtekno', methods=['POST'])
def confirm_tekno():
    result = request.form
    conn = get_db_connection()
    sql = ''' INSERT INTO tekno(artistId, artistName, ressourceUrl, lastView) VALUES(?,?,?,?) '''
    data = (result['artistId'], result['artistName'], result['ressourceUrl'], time.time())
    conn.execute(sql, data)
    conn.commit()
    conn.close()
    return render_template('confirmation_tekno.html', artist=result)


def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


if __name__ == "__main__":
    app.run()
