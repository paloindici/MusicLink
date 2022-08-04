import eyed3
import requests


def set_song_property(folder, albumArtist, artist, album, title, year, genre, position):
    """
    Writes a track's information to its settings
    :param folder : Folder link to track
    :param albumArtist : Album artist name to be set
    :param artist : Artist name to be set
    :param album : Album name to be set
    :param title : Track title name to be set
    :param year : Year of the release
    :param genre : Musical genre of the release
    :param position : Position of the song in album
    :return: None
    """
    try:

        link = f'{folder}/{position} - {title}.mp3'
        audiofile = eyed3.load(link)
        audiofile.tag.artist = artist
        audiofile.tag.album = album
        audiofile.tag.album_artist = albumArtist
        audiofile.tag.title = title
        audiofile.tag.release_date = year
        audiofile.tag.genre = genre
        audiofile.tag.save()
        return True
    except:
        return False


def thumb(url, path):
    img_data = requests.get(url).content
    with open(f'{path}cover.jpg', 'wb') as handler:
        handler.write(img_data)
