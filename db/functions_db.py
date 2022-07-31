import sqlite3
import time


def get_db_connection(path):
    """
    Get the database connection
    :param path: Link to database
    :return: conn: Database connection object
    """
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def read_db_verify_if_exist(conn, master_id):
    """
    Checks if the album data already exists in database
    :param conn: Database connection object
    :param master_id: Master identifier
    :return: True if album exists, otherwise false
    """
    sql = """SELECT * FROM albums WHERE masterId=?"""
    cur = conn.cursor()
    cur.execute(sql, [master_id])

    rows = cur.fetchall()

    if rows:
        return rows
    else:
        return False


def read_db_non_traite(conn):
    """
    Reading the database in search of unprocessed artist
    :param conn: Database connection object
    :return: The list of unprocessed components, or false if everything has been processed
    """
    cur = conn.cursor()
    cur.execute("SELECT * FROM albums WHERE lastView=0")

    rows = cur.fetchall()

    if rows:
        return rows
    else:
        return False


def update_db_traite(conn, master_id):
    """
    Update timestamp in the database when the artist's albums were processed
    :param conn: Database connection object
    :param master_id: Master identifier
    :return: None
    """
    sql = ''' UPDATE albums SET lastView = ? WHERE master_id = ?'''
    data = (time.time(), master_id)
    cur = conn.cursor()
    cur.execute(sql, data)
    conn.commit()


def write_db_new_item(conn, title, release_id, release_resource_url, release_uri, format, genre, master_id, master_url, songStyle):
    """
    Write new item in the database
    :param conn: Database connection object
    :param title: Release title
    :param release_id: Release identifier
    :param release_resource_url: Release Resource URL
    :param release_uri: Release URL
    :param format: Release format
    :param genre: Release music style
    :param master_id: Master identifier
    :param master_url: Master URL
    :param songStyle: Style of the song
    :return: None
    """
    sql = ''' INSERT INTO albums(title, releaseId, releaseResourceUrl, releaseUri, format, genre, masterId, masterUrl, lastView, songStyle) VALUES(?,?,?,?,?,?,?,?,?,?) '''
    data = (title, release_id, release_resource_url, release_uri, format, genre, master_id, master_url, 0, songStyle)
    cur = conn.cursor()
    cur.execute(sql, data)
    conn.commit()
