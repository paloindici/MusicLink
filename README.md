# MusicLink

Application to search and download music by albums.

The search database is Discogs, the largest music database on the web.

## Getting Started

These instructions will cover usage information and for the docker container 

### Prerequisities

In order to run this container you'll need docker installed.

* [Windows](https://docs.docker.com/windows/started)
* [OS X](https://docs.docker.com/mac/started/)
* [Linux](https://docs.docker.com/linux/started/)

### Usage

#### Container Parameters

Docker Compose

```shell
version: "3.9"
services:
  musiclink:
    image: paloindici/musiclink
    container_name: MusicLink
    labels:
      - com.centurylinklabs.watchtower.enable=true
    volumes:
      - /volume1/docker/MusicLink/data:/data
      - /volume1/music:/music
    ports:
      - 5000:5000
    restart: unless-stopped
```

#### Environment Variables

* `FLASK_ENV` - For developpement with server hot refresh and debug line. Also blocks items from being added to the database and does not initiate downloads (`production` by default, `development` for dev) OPTIONAL

#### Volumes

At least two volumes are required. One for app data, and one for music storage. 

If you have multiple audio libraries on Plex, you can create one volume per library to store them in different locations.

* `/data` - To store database and configuration file. REQUIRED
* `/music` - To store downloaded music. You can give it the name you want, it will be configurable in the MusicLink parameter menu. AT LEAST ONE REQUIRED

## Built With

* Flask v2.1.2
* PlexAPI v4.10.1
* discogs-client v2.3.0
* youtube-dl v2021.12.17
* eyed3 v0.9.6

## Find Us

* [Docker](https://hub.docker.com/repository/docker/paloindici/musiclink)

## Authors

* **paloindici** - *Initial work, python, HTML and docker* - [paloindici](https://github.com/jordanboucher42)
* **Jack6tm** - *HTML, CSS and JavaScript* - [Jack6tm](https://github.com/Jack6tm)

## License

This project is licensed under the Apache 2.0 License - see the [LICENSE.md](https://github.com/jordanboucher42/MusicLink/blob/master/LICENSE.md) file for details.