import json
import os

import requests
from ratelimit import limits, sleep_and_retry

ONE_MINUTE = 60
MAX_CALLS_PER_MINUTE = 60
base_url = 'https://api.discogs.com/'

DISCOGS_TOKEN = os.getenv('DISCOGS_TOKEN')


@sleep_and_retry
@limits(calls=MAX_CALLS_PER_MINUTE, period=ONE_MINUTE)
def getApi(url):
    """
    Global Discogs API call function with request module
    :param url : URL to get the information you are looking for
    :return : The API response
    """
    headers = {
        'User-Agent': 'MusicLink/1.0 +https://github.com/jordanboucher42/MusicLink',
        'Authorization': 'Discogs token=' + DISCOGS_TOKEN
    }

    response = requests.get(url, headers=headers, timeout=10)
    # print(f"{url}: {response.status_code}")

    if response.status_code == 200:
        result = json.loads(response.text)
        return result
    else:
        return None


def search(name, format, type='release', per_page=100, page=1):
    """
    Rechercher un artiste dans la base de donnée de discogs
    :param name : Nom de l'artiste à rechercher
    :param format : Format de la recherche ex: vinyl, cd, ...
    :param type : Type de la recherche
    :param per_page : Nombre de résultats souhaiter par page
    :param page : Numéro de la page à afficher
    :return : Liste des artistes trouvés
    """
    final_name = name.replace(" ", "%20")
    return getApi(f'{base_url}database/search?q={final_name}'
                  f'&type={type}'
                  f'&format={format}'
                  f'&per_page={per_page}'
                  f'&page={page}')


def artist(id, sort='year', sort_order='desc', per_page=100, page=1):
    """
    Rechercher les sorties d'un artiste dans la base de donnée de discogs
    :param id : Id de l'artiste à rechercher
    :param sort : Type de tri des résultats
    :param sort_order : Sens de tri des résultats
    :param per_page : Nombre de résultats souhaiter par page
    :param page : Numéro de la page à afficher
    :return : Liste des sorties de l'artiste
    """
    return getApi(f'{base_url}/artists/{id}/releases?sort={sort}'
                  f'&sort_order={sort_order}'
                  f'&per_page={per_page}'
                  f'&page={page}')
