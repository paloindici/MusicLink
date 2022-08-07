import json
import os
from os.path import exists

import api_discogs
from db import functions_db


def view_new_added(plex, library_name):
    """
    Get the recently added in Plex
    :param plex: The Plex server
    :param library_name: The list of the library name
    :return: Dictionary of albums recently added to Plex in the various libraries
    """
    recently_added = {}
    library_name = list(library_name.split(","))
    for library in library_name:
        recently = plex.library.section(library).recentlyAddedAlbums(maxresults=20)
        recently_added[library] = []
        for i in recently:
            recently_added[library].append({'title': i.title,
                                            'artist': i.artist().title,
                                            'thumb': i.posterUrl,
                                            'year': i.year})
    # print(recently_added)
    return recently_added


def search_result(form_search, location_db, discogs_token):
    """
    Search the result on discogs
    :param form_search: Value of the search formulaire
    :param location_db: Location of the database
    :param discogs_token: Token Discogs
    :return: List of the response from discogs
    """
    format = {
        1: 'CD',
        2: 'Vinyl',
        3: 'Cassette'
    }
    list_master_id = []
    final_list = []

    response = api_discogs.search(form_search['nom'], format[int(form_search['format'])], discogs_token)
    response_result = response['results']
    for album in response_result:
        if not album['master_id'] in list_master_id:
            final_list.append(album)
            if album['master_id'] != 0:
                list_master_id.append(album['master_id'])

    # Analyse de la DB pour savoir si déjà présent dans les demandes
    for item in final_list:
        if item['master_id'] != 0:
            exist = functions_db.read_db_verify_if_master_exist(functions_db.get_db_connection(location_db),
                                                                str(item['master_id']))
        else:
            exist = functions_db.read_db_verify_if_release_exist(functions_db.get_db_connection(location_db),
                                                                 str(item['id']))
        if exist:
            item['exist'] = True
        else:
            item['exist'] = False

    return final_list


def is_admin(plex, user):
    """
    Verify if connected user is Plex admin
    :param plex: Plex connection
    :param user: Connected username
    :return: True if Admin, or False
    """
    usernameAdmin = plex.myPlexAccount().username
    print(f"{usernameAdmin} -> {user}")
    if usernameAdmin == user:
        return True
    return False


def gestion_fichier_config():
    """
    Vérifie la présence d'un fichier de config (+ tentative de création si non trouvée) et retourne le chemin
    :return: Chemin exact ou le fichier de config est disponible
    """
    location_docker = "/data/config.json"
    location_windows = location_docker[6:]

    if not exists(location_docker) and not exists(location_windows):
        print(f"Fichier de config - Tentative de création sur le volume Docker...")
        try:
            os.path.join(location_docker)
            fichier = open(location_docker, "w")
            fichier.write("{}")
            fichier.close()
        except:
            print(
                f"Fichier de config - Erreur pendant la création du fichier {location_docker} sur le volume docker.")
        if os.path.isfile(location_docker):
            print(f"Fichier de config - Fichier {location_docker} existe maintenant sur le volume docker.")
            return location_docker

        print(f"Fichier de config - Tentative de création sur Windows...")
        try:
            os.path.join(location_windows)
            fichier = open(location_windows, "w")
            fichier.write("{}")
            fichier.close()
        except:
            print(f"Fichier de config - Erreur pendant la création du fichier {location_windows} sur windows.")
        if os.path.isfile(location_windows):
            print(f"Fichier de config - Fichier {location_windows} existe maintenant sur Windows.")
            return location_windows
        else:
            print(f"Fichier de config - Fichier {location_windows} n'existe toujours pas sur Windows.")
            print(f"Impossible de créer ou d'accéder a un fichier de config")
            return None
    elif exists(location_docker):
        return location_docker
    else:
        return location_windows


def verify_config(location_config):
    """
    Vérifie que la configuration minumum soit prête
    :return: True si la config est prête, sinon False
    """
    with open(location_config) as outfile:
        datas = json.load(outfile)
        if "plex_url" in datas and "plex_token" in datas and "discogs_token" in datas:
            return True
        return False


def read_config_content(location_config):
    """
    Lis le fichier de configuration et retourne son contenu
    :param location_config : Lien d'accès au fichier de config
    :return: Contenu du fichier de configuration
    """
    with open(location_config) as outfile:
        datas = json.load(outfile)
        return datas


def write_config(location_config, new_datas):
    """
    Écrit le fichier de configuration
    """
    with open(location_config) as outfile:
        datas = json.load(outfile)
    datas['plex_url'] = new_datas['plex_url']
    datas['plex_token'] = new_datas['plex_token']
    datas['discogs_token'] = new_datas['discogs_token']
    with open(location_config, "w") as outfile:
        json.dump(datas, outfile, indent=4)


def read_config(location_config, key):
    """
    Lis le fichier de configuration et retourne une valeur de son contenu
    :param location_config : Lien d'accès au fichier de config
    :param key : Clé de la valeur recherchée
    :return: Valeur de la clé recherchée ou None si inexistant
    """
    with open(location_config) as outfile:
        datas = json.load(outfile)
        if key in datas:
            return datas[key]
        return None
