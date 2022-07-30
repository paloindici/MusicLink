import os
import sqlite3
from flask import Flask, render_template, request, session, redirect, url_for
from plexapi.server import PlexServer
from plexapi.myplex import MyPlexAccount

import api_discogs
import scraper_discogs
import thread_downloader
from db import init_db

# Config de Flask
app = Flask(__name__)
app.config.from_pyfile('config.py')
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# Config des API - services externes
PLEX_TOKEN = os.getenv('PLEX_TOKEN')
BASE_URL_PLEX = os.getenv('BASE_URL_PLEX')
plex = PlexServer(BASE_URL_PLEX, PLEX_TOKEN)

# Création de la DB au démarrage si inexistante
location_db = init_db.gestion_fichier_database()
if location_db is None:
    print("Erreur : Musiclink s'arrête car il est impossible de trouver ou de créer"
          "une base de donnée dès l'initialisation de l'application.")
    exit()

# Création d'une tache parallèle pour la gestion des téléchargements
# thread_downloader = thread_downloader.Thread_main_downloader(1, "Main-dl")
# thread_downloader.start()


# Page d'accueil de MusicLink
@app.route('/')
def index():
    if 'token' in session:
        user = MyPlexAccount(token=session['token']).username

        recentMusique = plex.library.section('Musique').recentlyAddedAlbums(maxresults=10)
        recentTekno = plex.library.section('Tekno').recentlyAddedAlbums(maxresults=10)

        recentAdded = []

        for i in range(len(recentMusique)):
            recentAdded.append({'title': recentMusique[i].title,
                                'artist': recentMusique[i].artist().title,
                                'thumb': recentMusique[i].posterUrl,
                                'year': recentMusique[i].year})

        for i in range(len(recentTekno)):
            recentAdded.append({'title': recentTekno[i].title,
                                'artist': recentTekno[i].artist().title,
                                'thumb': recentTekno[i].posterUrl,
                                'year': recentTekno[i].year})

        return render_template('index.html', data=recentAdded, username=user)
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
            error = "adresse email ou mot de passe incorect"
            return render_template('login.html', error=error)

        try:
            userToken = MyPlexAccount(userEmail, userPass).authenticationToken
        except Exception as err:
            # TODO var err in log
            error = "adresse email ou mot de passe incorect"
            return render_template('login.html', error=error)

        session['token'] = userToken
        return redirect(url_for('index'))

    return render_template('login.html', error=error)


@app.route('/signout')
def signout():
    session.clear()
    return redirect(url_for('signin'))


@app.route('/result/search', methods=['GET'])
def search_result():
    if 'token' in session:
        format = {
            1: 'CD',
            2: 'Vinyl',
            3: 'Cassette'
        }
        list_master_id = []
        final_list = []
        user = MyPlexAccount(token=session['token']).username
        result = request.args
        response = api_discogs.search(result['nom'], format[int(result['format'])])
        response_result = response['results']
        for album in response_result:
            if not album['master_id'] in list_master_id:
                list_master_id.append(album['master_id'])
                final_list.append(album)
            if len(final_list) == 25:
                break
        # print(response)
        # print(final_list)
        pagination = response['pagination']
        pagination['items'] = len(final_list)
        # print(pagination)

        for album in final_list:
            thumb = scraper_discogs.get_thumb(f"https://www.discogs.com/fr{album['uri']}")
            album['thumb'] = thumb

        # Analyse de la DB pour savoir si déjà présent dans les demandes
        # conn = get_db_connection()
        # cur = conn.cursor()
        # for resultArtist in resultSearch:
        #     cur.execute("SELECT * FROM artistTekno WHERE artistId=?", [(str(resultArtist.data['id']))])
        #     rows = cur.fetchall()
        #     if rows:
        #         print("present")
        #         resultArtist.data['exist'] = True
        #     conn.commit()
        #     print(resultArtist.data)
        # conn.close()

        print(final_list)
        return render_template("recherche.html", datas=final_list, pagination=pagination, username=user)
    else:
        return redirect(url_for('signin'))


# Page de confirmation de l'ajout d'un album
@app.route('/result/confirmed', methods=['POST'])
def confirm_add():
    if 'token' in session:
        result = request.form
        print(result)
        print(result['title'])
        # conn = get_db_connection()
        # sql = ''' INSERT INTO artistTekno(artistId, artistName, ressourceUrl, lastView) VALUES(?,?,?,?) '''
        # data = (result['artistId'], result['artistName'], result['ressourceUrl'], 0)
        # conn.execute(sql, data)
        # conn.commit()
        # conn.close()

        return render_template('confirmation.html', data=result)
    else:
        return redirect(url_for('signin'))


# Fonction de connection a la base de donnée
def get_db_connection():
    conn = sqlite3.connect(location_db)
    conn.row_factory = sqlite3.Row
    return conn


if __name__ == "__main__":
    app.run(host='0.0.0.0')
