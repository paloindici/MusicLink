import os
from flask import Flask, render_template, request, session, redirect, url_for
from plexapi.server import PlexServer
from plexapi.myplex import MyPlexAccount

import api_discogs
import tools
from db import init_db, functions_db
from downloader import thread_downloader

# Config de Flask
app = Flask(__name__)
app.config.from_pyfile('config.py')
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# Config generale de musiclink
location_config = tools.gestion_fichier_config()

# Memoire pour les erreur au démarrage de plex et discogs
plex_error = True
discogs_error = True

# Config des API - services externes
PLEX_TOKEN = tools.read_config(location_config, 'plex_token')
BASE_URL_PLEX = tools.read_config(location_config, 'plex_url')
DISCOGS_TOKEN = tools.read_config(location_config, 'discogs_token')
LIBRARY = tools.read_config(location_config, 'library')
CONTACT_URL = tools.read_config(location_config, 'contact_url')
FLASK_ENV = os.getenv('FLASK_ENV', 'production')

try:
    plex = PlexServer(BASE_URL_PLEX, PLEX_TOKEN)
    plex_error = False
except:
    plex_error = True

try:
    api_discogs.search('nirvanna', 'CD', DISCOGS_TOKEN)
    discogs_error = False
except:
    discogs_error = True

# Création de la DB au démarrage si inexistante
location_db = init_db.gestion_fichier_database()
if location_db is None:
    print("Erreur : Musiclink s'arrête car il est impossible de trouver ou de créer"
          "une base de donnée dès l'initialisation de l'application.")
    exit()

# Création d'une tache parallèle pour la gestion des téléchargements
thread_downloader = thread_downloader.Thread_main_downloader(1, "Main-dl", location_db, DISCOGS_TOKEN, location_config)
if not thread_downloader.is_alive() and FLASK_ENV != 'development' and not plex_error and not discogs_error:
    thread_downloader.start()


# Page d'accueil de MusicLink
@app.route('/')
def index():
    if not tools.verify_config(location_config) or plex_error or discogs_error:
        return render_template('demarrage.html', datas=tools.read_config_all(location_config))
    if 'token' in session:
        user = MyPlexAccount(token=session['token']).username
        is_admin = tools.is_admin(plex, user)

        recently_added = tools.view_new_added(plex, LIBRARY)

        return render_template('index.html', data=recently_added, username=user, isadmin=is_admin, contact=CONTACT_URL)
    else:
        return redirect(url_for('signin'))


@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if not tools.verify_config(location_config) or plex_error or discogs_error:
        return render_template('demarrage.html', datas=tools.read_config_all(location_config))
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
    if not tools.verify_config(location_config) or plex_error or discogs_error:
        return render_template('demarrage.html', datas=tools.read_config_all(location_config))
    session.clear()
    return redirect(url_for('signin'))


@app.route('/settings', methods=['GET'])
def settings():
    if not tools.verify_config(location_config) or plex_error or discogs_error:
        return render_template('demarrage.html', datas=tools.read_config_all(location_config))
    if 'token' in session:
        user = MyPlexAccount(token=session['token']).username
        is_admin = tools.is_admin(plex, user)
        if not is_admin:
            return redirect(url_for('index'))

        plex_lib = tools.list_music_library(plex)
        config = tools.read_config_all(location_config)

        datas = {
            'plex_url': BASE_URL_PLEX,
            'plex_token': PLEX_TOKEN,
            'discord_token': DISCOGS_TOKEN,
            'plex_lib': plex_lib,
        }
        if 'contact_url' in config:
            datas['contact_url'] = config['contact_url']

        if 'library' in config:
            for lib in plex_lib:
                for item in config['library']:
                    if item['name'] == lib:
                        datas[lib] = item['path']
                        break
        print(datas)

        return render_template('configuration.html', datas=datas, username=user, isadmin=is_admin, contact=CONTACT_URL)
    else:
        return redirect(url_for('signin'))


@app.route('/valid_settings', methods=['POST'])
def valid_settings():
    if not tools.verify_config(location_config) or plex_error or discogs_error:
        return render_template('demarrage.html', datas=tools.read_config_all(location_config))
    if 'token' in session:
        user = MyPlexAccount(token=session['token']).username
        if not tools.is_admin(plex, user):
            return redirect(url_for('index'))

        result = request.form.to_dict()
        global PLEX_TOKEN, BASE_URL_PLEX, DISCOGS_TOKEN, CONTACT_URL
        PLEX_TOKEN = result['plex_token']
        BASE_URL_PLEX = result['plex_url']
        DISCOGS_TOKEN = result['discogs_token']
        CONTACT_URL = result['contact_url']
        tools.write_config_all(location_config, result)

        return redirect(url_for('index'))
    else:
        return redirect(url_for('signin'))


@app.route('/result/search', methods=['GET'])
def search_result():
    if not tools.verify_config(location_config) or plex_error or discogs_error:
        return render_template('demarrage.html', datas=tools.read_config_all(location_config))
    if 'token' in session:
        user = MyPlexAccount(token=session['token']).username
        is_admin = tools.is_admin(plex, user)
        result = request.args
        final_list = tools.search_result(result, location_db, DISCOGS_TOKEN)
        number = len(final_list)
        # library_name = list(LIBRARY_NAME.split(","))
        library_name = []
        for lib in LIBRARY:
            library_name.append(lib['name'])

        # print(final_list)
        return render_template("recherche.html", datas=final_list, number=number, library_name=library_name,
                               username=user, isadmin=is_admin, contact=CONTACT_URL)
    else:
        return redirect(url_for('signin'))


# Page de confirmation de l'ajout d'un album
@app.route('/result/confirmed', methods=['POST'])
def confirm_add():
    if not tools.verify_config(location_config) or plex_error or discogs_error:
        return render_template('demarrage.html', datas=tools.read_config_all(location_config))
    if 'token' in session:
        user = MyPlexAccount(token=session['token']).username
        is_admin = tools.is_admin(plex, user)
        result = request.form.to_dict()
        # print(result)
        if FLASK_ENV != 'development':
            functions_db.write_db_new_item(functions_db.get_db_connection(location_db), result['title'], result['id'],
                                           result['resource_url'], result['uri'], result['format'], result['genre'],
                                           result['master_id'], result['master_url'], result['songStyle'])

        return render_template('confirmation.html', datas=result, username=user, isadmin=is_admin, contact=CONTACT_URL)
    else:
        return redirect(url_for('signin'))


# Écrit la configuration du premier démarrage
@app.route('/writeconfig', methods=['POST'])
def writeconfig():
    global plex, plex_error, discogs_error, PLEX_TOKEN, BASE_URL_PLEX, DISCOGS_TOKEN
    result = request.form.to_dict()
    print(result)
    tools.write_config(location_config, result)

    PLEX_TOKEN = result['plex_token']
    BASE_URL_PLEX = result['plex_url']
    DISCOGS_TOKEN = result['discogs_token']

    test_discogs = api_discogs.search('nirvanna', 'CD', DISCOGS_TOKEN)
    if test_discogs is not None:
        discogs_error = False
    else:
        discogs_error = True

    try:
        plex = PlexServer(BASE_URL_PLEX, PLEX_TOKEN)
        plex_error = False
    except:
        plex_error = True

    if not plex_error and not discogs_error:
        return redirect(url_for('signin'))
    else:
        return render_template('demarrage.html',
                               datas=tools.read_config_all(location_config),
                               plex_error=plex_error,
                               discogs_error=discogs_error)


if __name__ == "__main__":
    app.run(host='0.0.0.0')
