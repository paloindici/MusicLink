import threading

import api_discogs
from db import functions_db
from downloader import youtube, tools_dl

exitFlag = 0


class Thread_main_downloader(threading.Thread):
    def __init__(self, threadID, name, chemin_db):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.chemin_db = chemin_db

    def run(self):
        non_traite = functions_db.read_db_non_traite(functions_db.get_db_connection(self.chemin_db))
        print("Item non traités:")
        for item in non_traite:
            release = api_discogs.release(item['releaseId'])
            print(release)
            release['artists_sort'] = release['artists_sort'].replace("/", "&")
            folder = f"{release['artists_sort']} - {release['title']}"

            for i, track in enumerate(release['tracklist']):
                succes_dl = False
                if len(release['tracklist']) == len(release['videos']):
                    # Download with direct URL
                    title = f"{track['position']} - {track['title']}"
                    succes_dl = youtube.youtube_download(folder, title, release['videos'][i]['uri'])
                    print(f"succès: {succes_dl}")
                else:
                    # Search on youtube
                    title = f"{track['position']} - {track['title']}"
                    result = youtube.youtube_search(f"{track['artists'][0]['name']} {track['title']}")
                    # !!!!!!!!!!!! FONCTION POUR VERIFIER LE RESULTAT DE LA RECHERCHE DE PLUSIEURS MANIÈRE AFFIN D'ETRE SUR DU RESULTAT!!!!!!!!!!!
                    # succes_dl = youtube.youtube_download(folder, title, result['webpage_url'])
                    print(f"succès download : {succes_dl}")

                if succes_dl:
                    # RETAG
                    genre = ""
                    for j, item in enumerate(release['genres']):
                        genre += item
                        if j + 1 < len(release['genres']):
                            genre += "; "
                    succes_tag = tools_dl.set_song_property(folder=f'./music/{folder}',
                                                            albumArtist=release['artists_sort'].replace(" & ", "; "),
                                                            artist=track['artists'][0]['name'],
                                                            album=release['title'],
                                                            title=track['title'],
                                                            year=release['year'],
                                                            genre=genre,
                                                            position=track['position'])
                    print(f"succès retags : {succes_tag}")

            # ALBUM THUMB
            tools_dl.thumb(release['thumb'], f'./music/{folder}/')
            break
