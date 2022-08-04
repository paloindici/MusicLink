import youtube_dl
import requests

# Doc: https://github.com/ytdl-org/youtube-dl

# ydl_opts = {
#         'format': 'bestaudio/best',
#         'cachedir': False,
#         'postprocessors': [{
#             'key': 'FFmpegExtractAudio',
#             'preferredcodec': 'mp3',
#             'preferredquality': '320',
#         }],
#         'outtmpl': f'/music/{artist}/{album}/{title}.%%(ext)s'
#     }

ydl_opts = {
    'format': 'bestaudio/best',
    'cachedir': False,
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '320',
    }]
}


def youtube_search(arg):
    """
    Search video on youtube
    :param arg: Keyword for search
    :return: None
    """
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            requests.get(arg)
        except:
            video = ydl.extract_info(f"ytsearch:{arg}", download=False)['entries'][0]
        else:
            video = ydl.extract_info(arg, download=False)
    return video


def youtube_download(folder, title, link):
    """
    Launch downloading song from Youtube link
    :param folder: Folder link for save download
    :param title: Artist name to download
    :param link: Album name to download
    :return: None
    """
    ydl_opts['outtmpl'] = f'/music/{folder}/{title}.%%(ext)s'
    # Lancer le téléchargement dans une boucle de maximum 10 tentative pour contrer les erreurs 403
    i = 1
    while i <= 10:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            try:
                # ydl.cache.remove()
                print(f"({i}/10) Démarrage du téléchargement: {folder} - {title} - {link}")
                ydl.download([link])
                return True
            except youtube_dl.DownloadError as error:
                pass
        i += 1
    return False
