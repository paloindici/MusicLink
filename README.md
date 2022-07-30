# MusicLink
Link for Plex, Discogs, Youtube and more.

The identification is done via a plex account, and checks the authorization of the account in your server

## Setup for Production
### **.env example:**
Example of required configuration file:

`DISCOGS_TOKEN=<token_of_your_discogs_account>` REQUIRED

`PLEX_TOKEN=<token_of_your_plex_server>` REQUIRED

`BASE_URL_PLEX=<url_of_your_plex_server>` REQUIRED

`FLASK_ENV=development` REQUIRED

## Development
### **Rebuild Requirement:**
`pip freeze > requirements.txt`

### **Install Requirement:**
`pip install -r requirements.txt`