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


def search_result(form_search, location_db):
    """
    Search the result on discogs
    :param form_search: Value of the search formulaire
    :param location_db: Location of the database
    :return: List of the response from discogs
    """
    format = {
        1: 'CD',
        2: 'Vinyl',
        3: 'Cassette'
    }
    list_master_id = []
    final_list = []

    response = api_discogs.search(form_search['nom'], format[int(form_search['format'])])
    response_result = response['results']
    for album in response_result:
        if not album['master_id'] in list_master_id:
            list_master_id.append(album['master_id'])
            final_list.append(album)

    # Analyse de la DB pour savoir si déjà présent dans les demandes
    for item in final_list:
        exist = functions_db.read_db_verify_if_exist(functions_db.get_db_connection(location_db),
                                                     str(item['master_id']))
        if exist:
            item['exist'] = True
        else:
            item['exist'] = False

    return final_list
