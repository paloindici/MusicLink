import json
import os
from os.path import exists

import api_discogs
from db import functions_db
from discord_webhook import DiscordWebhook, DiscordEmbed


def view_new_added(plex, library):
    """
    Get the recently added in Plex
    :param plex: The Plex server
    :param library: The list of the library
    :return: Dictionary of albums recently added to Plex in the various libraries
    """
    recently_added = {}
    if library is not None:
        for lib in library:
            recently = plex.library.section(lib).recentlyAddedAlbums(maxresults=20)
            recently_added[lib] = []
            for i in recently:
                recently_added[lib].append({'title': i.title,
                                            'artist': i.artist().title,
                                            'thumb': i.posterUrl,
                                            'year': i.year})
        return recently_added
    else:
        return


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
    response = api_discogs.search(form_search['nom'], format[int(form_search['format'])], discogs_token, type='label')
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


def indexage_search_result(name, location_db, discogs_token):
    """
    Search the result on discogs
    :param name: Name of the release
    :param location_db: Location of the database
    :param discogs_token: Token Discogs
    :return: List of the response from discogs
    """
    list_master_id = []
    final_list = []

    response = api_discogs.search(name, 'CD', discogs_token)
    response_result = response['results']
    for album in response_result:
        if not album['master_id'] in list_master_id:
            final_list.append(album)
            if album['master_id'] != 0:
                list_master_id.append(album['master_id'])
    response = api_discogs.search(name, 'CD', discogs_token, type='label')
    response_result = response['results']
    for album in response_result:
        if not album['master_id'] in list_master_id:
            final_list.append(album)
            if album['master_id'] != 0:
                list_master_id.append(album['master_id'])
    response = api_discogs.search(name, 'Vinyl', discogs_token)
    response_result = response['results']
    for album in response_result:
        if not album['master_id'] in list_master_id:
            final_list.append(album)
            if album['master_id'] != 0:
                list_master_id.append(album['master_id'])
    response = api_discogs.search(name, 'Vinyl', discogs_token, type='label')
    response_result = response['results']
    for album in response_result:
        if not album['master_id'] in list_master_id:
            final_list.append(album)
            if album['master_id'] != 0:
                list_master_id.append(album['master_id'])

    return final_list


def is_admin(plex, user):
    """
    Verify if connected user is Plex admin
    :param plex: Plex connection
    :param user: Connected username
    :return: True if Admin, or False
    """
    usernameAdmin = plex.myPlexAccount().username
    # print(f"{usernameAdmin} -> {user}")
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

    print('Lancement gestion fichier config.json')

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
        print('fichier present sur docker')
        return location_docker
    else:
        print('fichier present sur windows')
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


def write_config_all(location_config, new_datas):
    """
    Écrit le fichier de configuration
    """
    with open(location_config) as outfile:
        datas = json.load(outfile)
    datas['plex_url'] = new_datas['plex_url']
    datas['plex_token'] = new_datas['plex_token']
    datas['discogs_token'] = new_datas['discogs_token']
    datas['contact_url'] = new_datas['contact_url']
    datas['webhook_url'] = new_datas['webhook_url']
    if 'webhook_add' in new_datas:
        datas['webhook_add'] = True
    else:
        datas['webhook_add'] = False
    if 'webhook_added' in new_datas:
        datas['webhook_added'] = True
    else:
        datas['webhook_added'] = False
    new_datas.pop('plex_url', None)
    new_datas.pop('plex_token', None)
    new_datas.pop('discogs_token', None)
    new_datas.pop('contact_url', None)
    new_datas.pop('webhook_url', None)
    new_datas.pop('webhook_add', None)
    new_datas.pop('webhook_added', None)
    datas['library'] = []
    for lib in new_datas:
        if lib[:3] == 'lib':
            lib_name = lib[4:]
            lib = {
                'name': lib_name,
                'path': new_datas['path_' + lib_name]
            }
            datas['library'].append(lib)
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


def read_config_all(location_config):
    """
    Lis le fichier de configuration et retourne son contenu
    :param location_config : Lien d'accès au fichier de config
    :return: Contenu du fichier de configuration
    """
    with open(location_config) as outfile:
        datas = json.load(outfile)
        return datas


def list_music_library(plex):
    """
    Recherche de toutes les librairies de musique disponible sur Plex
    :param plex : Objet de connection Plex
    :return: Liste des nom des librairies musique
    """
    music_section = []
    sections = plex.library.sections()
    for section in sections:
        if section.CONTENT_TYPE == "audio":
            music_section.append(section.title)
    # print(music_section)
    return music_section


def webhook_send(url, stat, datas, username=None):
    """
    Envoi un embed sur discord pour chaque nouveau contenu demandé
    :param url : URL du webhook Discord
    :param stat : Boolean si la fonction est activée ou pas
    :param datas : Dictionnaire des informations sur le contenu demandé
    :param username : Pseudo de la personne qui a fait la demande
    """
    if stat:
        if url is not None and url != "":
            try:
                webhook = DiscordWebhook(url=url)

                if username is not None:
                    description = "Un nouveau contenu audio a été demandé !"
                else:
                    description = "Un nouveau contenu est disponible"

                embed = DiscordEmbed(title=f"{datas['title']}",
                                     url=f"https://www.discogs.com/fr{datas['uri']}",
                                     description=f"{description}",
                                     color="9c59b6")
                embed.set_footer(text="Powered by: MusicLink")
                embed.set_timestamp()
                if 'year' in datas and datas['year'] != '':
                    embed.add_embed_field(name="Année", value=f"{datas['year']}")
                if 'format' in datas and datas['format'] != '':
                    embed.add_embed_field(name="Support", value=f"{datas['format']}")
                if 'genre' in datas and datas['genre'] != '':
                    embed.add_embed_field(name="Genre", value=f"{datas['genre']}")
                if 'thumb' in datas and datas['thumb'] != '':
                    embed.set_thumbnail(url=f"{datas['thumb']}")
                if username is not None:
                    embed.add_embed_field(name="Demandé par", value=f"{username}", inline=False)

                webhook.add_embed(embed)
                response = webhook.execute()
                return
            except:
                return
        return
    return
