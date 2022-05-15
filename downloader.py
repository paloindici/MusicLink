import json
import urllib
from os import path

import eyed3
import youtube_dl

import app


def download(artist, album, title, link):
    print("Démarrage du téléchargement: " + artist + " - " + album + " - " + title + " - " + link)
    ydl_opts = {
        'format': 'bestaudio/best',
        'cachedir': False,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320',
        }],
        'outtmpl': f'/{artist}/{album}/{title}.%%(ext)s'
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            # ydl.cache.remove()
            ydl.download([link])
        except youtube_dl.DownloadError as error:
            pass


def get_tracks(artistId):
    artist = app.discogs.artist(artistId)
    # for i in range(artist.releases.count):
    for i in range(5):
        # print(artist.releases[i].data)
        albumArtistName = artist.releases[i].data['artist']
        albumArtistName = albumArtistName.replace("/", "-")
        albumTitle = artist.releases[i].data['title']
        albumTitle = albumTitle.replace("/", "-")
        albumId = str(artist.releases[i].data['id'])
        albumTrackCount = str(len(artist.releases[i].tracklist))
        albumTrackList = str(artist.releases[i].tracklist)
        albumType = artist.releases[i].data['type']
        albumRessourceUrl = 'https://api.discogs.com/' + albumType + 's/' + albumId
        # print("Nom de l'artiste:" + albumArtistName)
        # print("Nom de l'album: " + albumTitle)
        # print("ID de l'album: " + albumId)
        # print("Nombre de musique dans l'album: " + albumTrackCount)
        # print("Liste des musiques de l'album: " + albumTrackList)
        # print("Type de l'album: " + albumType)
        # print("URL de ressource de l'album: " + albumRessourceUrl)

        albumRessources = urllib.request.urlopen(albumRessourceUrl)
        data = albumRessources.read()
        data = json.loads(data.decode('utf-8'))
        print(data)
        # print(json.dumps(data, indent=4, separators=(',', ': '), sort_keys=True))

        if not verify_if_exist(albumArtistName, albumTitle):
            print(f"{albumArtistName} - {albumTitle} n'existe pas")
            for j in range(len(data['videos'])):
                print(len(data['artists']))
                if len(data['artists']) == 1:
                    songArtist = data['artists'][0]['name']
                else:
                    songArtist = data['tracklist'][j]['artists'][0]['name']
                songName = data['videos'][j]['title']
                songLink = data['videos'][j]['uri']
                download(albumArtistName, albumTitle, songName, songLink)
                set_song_property(albumArtistName, songArtist, albumTitle, songName)
        else:
            print(f"{albumArtistName} - {albumTitle} existe déjà")


def verify_if_exist(artist, album):
    albumDir = "./" + artist + "/" + album
    return path.isdir(albumDir)


def set_song_property(albumArtist, artist, album, title):
    try:
        link = f'./{albumArtist}/{album}/{title}.mp3'
        audiofile = eyed3.load(link)
        audiofile.tag.artist = artist
        audiofile.tag.album = album
        audiofile.tag.album_artist = albumArtist
        audiofile.tag.title = title
        audiofile.tag.save()
    except:
        pass
