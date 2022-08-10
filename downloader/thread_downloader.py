import threading
import time

import api_discogs
import tools
from db import functions_db
from downloader import youtube, tools_dl

exitFlag = 0


class Thread_main_downloader(threading.Thread):
    def __init__(self, threadID, name, chemin_db, discogs_token, location_config):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.chemin_db = chemin_db
        self.discogs_token = discogs_token
        self.location_config = location_config
        self.last_run = 0

    def run(self):
        while True:
            # print(time.time() - self.last_run)
            if time.time() - self.last_run > 60:
                self.last_run = time.time()
                non_traite = functions_db.read_db_non_traite(functions_db.get_db_connection(self.chemin_db))
                if non_traite:
                    for item in non_traite:
                        path = ""
                        config_path = tools.read_config(self.location_config, "library")
                        for lib in config_path:
                            if lib['name'] == item['songStyle']:
                                path = lib['path']
                                break
                        release = api_discogs.release(item['releaseId'], self.discogs_token)
                        release['artists_sort'] = release['artists_sort'].replace("/", "&")
                        folder = f"{release['artists_sort']} - {release['title']}"

                        for i, track in enumerate(release['tracklist']):
                            succes_dl = False
                            if len(release['tracklist']) == len(release['videos']):
                                # Download with direct URL
                                title = f"{track['position']} - {track['title']}"
                                succes_dl = youtube.youtube_download(path, folder, title, release['videos'][i]['uri'])
                                print(f"succès: {succes_dl}")
                            else:
                                # Search on youtube
                                title = f"{track['position']} - {track['title']}"
                                result = youtube.youtube_search(f"{track['artists'][0]['name']} {track['title']}")
                                # !!!!!!!!!!!! FONCTION POUR VERIFIER LE RESULTAT DE LA RECHERCHE DE PLUSIEURS MANIÈRE AFFIN D'ETRE SUR DU RESULTAT!!!!!!!!!!!
                                succes_dl = youtube.youtube_download(path, folder, title, result['webpage_url'])

                            if succes_dl:
                                # RETAG
                                genre = ""
                                for j, k in enumerate(release['genres']):
                                    genre += k
                                    if j + 1 < len(release['genres']):
                                        genre += "; "
                                succes_tag = tools_dl.set_song_property(folder=f'.{path}/{folder}',
                                                                        albumArtist=release['artists_sort'].replace(" & ", "; "),
                                                                        artist=track['artists'][0]['name'],
                                                                        album=release['title'],
                                                                        title=track['title'],
                                                                        year=release['year'],
                                                                        genre=genre,
                                                                        position=track['position'])

                        # ALBUM THUMB
                        try:
                            tools_dl.thumb(release['thumb'], f'.{path}/{folder}/')
                        except:
                            pass

                        # VALID TOTAL DOWNLOAD
                        functions_db.update_db_traite(functions_db.get_db_connection(self.chemin_db), item['releaseId'])
