import asyncio
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
        #print("Complete auth at URL: {}".format(plexauth.auth_url()))
        token = await plexauth.token()

    if token:
        print("Token: {}".format(token))
    else:
        print("No token returned.")


loop = asyncio.get_event_loop()
loop.run_until_complete(oauth())
