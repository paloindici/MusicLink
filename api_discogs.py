import json

import requests
from ratelimit import limits, sleep_and_retry

# Doc : https://www.discogs.com/developers

ONE_MINUTE = 60
MAX_CALLS_PER_MINUTE = 60
base_url = 'https://api.discogs.com/'


@sleep_and_retry
@limits(calls=MAX_CALLS_PER_MINUTE, period=ONE_MINUTE)
def getApi(url, discogs_token):
    """
    Global Discogs API call function with request module
    :param url : URL to get the information you are looking for
    :param discogs_token: Token Discogs
    :return : The API response
    """
    headers = {
        'User-Agent': 'MusicLink/1.0 +https://github.com/jordanboucher42/MusicLink',
        'Authorization': 'Discogs token=' + discogs_token
    }

    response = requests.get(url, headers=headers, timeout=10)
    # print(f"{url}: {response.status_code}")

    if response.status_code == 200:
        result = json.loads(response.text)
        return result
    else:
        return None


def search(name, format, discogs_token, type='release', per_page=100, page=1):
    """
    Search in the discogs database
    :param name : Album title
    :param format : Search Format ex: vinyl, cd, ...
    :param type : Type of research
    :param per_page : Number of desired results per page
    :param page : Page number to display
    :param discogs_token : Token Discogs
    :return : Discogs API search answer
    """
    final_name = name.replace(" ", "%20")
    return getApi(f'{base_url}database/search?q={final_name}'
                  f'&type={type}'
                  f'&format={format}'
                  f'&per_page={per_page}'
                  f'&page={page}', discogs_token)


def release(id, discogs_token):
    """
    Retrieve album information from Discogs
    :param id : Release ID
    :param discogs_token : Token Discogs
    :return : Release details
    """
    return getApi(f'{base_url}releases/{id}', discogs_token)
