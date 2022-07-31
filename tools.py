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
    print(recently_added)
    return recently_added
