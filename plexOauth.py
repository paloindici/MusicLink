import webbrowser

from plexauth import PlexAuth

PAYLOAD = {
    'X-Plex-Product': 'MusicLink',
    'X-Plex-Version': '0.0.1',
    'X-Plex-Device': 'Test Device',
    'X-Plex-Platform': 'Test Platform',
    'X-Plex-Device-Name': 'Test Device Name',
    'X-Plex-Device-Vendor': 'Test Vendor',
    'X-Plex-Model': 'Test Model',
    'X-Plex-Client-Platform': 'Test Client Platform'
}


async def oauth():
    async with PlexAuth(PAYLOAD) as plexauth:
        await plexauth.initiate_auth()
        webbrowser.open_new_tab(plexauth.auth_url())
        token = await plexauth.token()
        return token
