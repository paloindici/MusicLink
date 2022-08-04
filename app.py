import os
from flask import Flask, render_template, request, session, redirect, url_for
from plexapi.server import PlexServer
from plexapi.myplex import MyPlexAccount

import tools
from db import init_db, functions_db
from downloader import thread_downloader

# Config de Flask
app = Flask(__name__)
app.config.from_pyfile('config.py')
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# Config des API - services externes
PLEX_TOKEN = os.getenv('PLEX_TOKEN')
BASE_URL_PLEX = os.getenv('BASE_URL_PLEX')
LIBRARY_NAME = os.getenv('LIBRARY_NAME')
DEBUG = os.getenv('DEBUG', '0')
plex = PlexServer(BASE_URL_PLEX, PLEX_TOKEN)

# Création de la DB au démarrage si inexistante
location_db = init_db.gestion_fichier_database()
if location_db is None:
    print("Erreur : Musiclink s'arrête car il est impossible de trouver ou de créer"
          "une base de donnée dès l'initialisation de l'application.")
    exit()

# Création d'une tache parallèle pour la gestion des téléchargements
thread_downloader = thread_downloader.Thread_main_downloader(1, "Main-dl", location_db)


# Page d'accueil de MusicLink
@app.route('/')
def index():
    if 'token' in session:
        user = MyPlexAccount(token=session['token']).username

        recently_added = tools.view_new_added(plex, LIBRARY_NAME)

        return render_template('index.html', data=recently_added, username=user)
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
        user = MyPlexAccount(token=session['token']).username
        result = request.args
        final_list = tools.search_result(result, location_db)
        number = len(final_list)
        library_name = list(LIBRARY_NAME.split(","))

        # print(final_list)
        return render_template("recherche.html", datas=final_list, number=number, library_name=library_name,
                               username=user)
    else:
        return redirect(url_for('signin'))


# Page de confirmation de l'ajout d'un album
@app.route('/result/confirmed', methods=['POST'])
def confirm_add():
    if 'token' in session:
        result = request.form.to_dict()
        # print(result)
        functions_db.write_db_new_item(functions_db.get_db_connection(location_db), result['title'], result['id'],
                                       result['resource_url'], result['uri'], result['format'], result['genre'],
                                       result['master_id'], result['master_url'], result['songStyle'])
        if DEBUG != '1' and DEBUG != 'true' and DEBUG is not True:
            thread_downloader.start()

        return render_template('confirmation.html', data=result)
    else:
        return redirect(url_for('signin'))


if __name__ == "__main__":
    app.run(host='0.0.0.0')
