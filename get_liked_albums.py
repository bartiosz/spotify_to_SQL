import requests
import sqlite3
from dotenv import load_dotenv
import os

from config import (
    LIBRARY
)

def get_saved_albums(ACCESS_TOKEN):
    # load_dotenv()
    # ACCESS_TOKEN = os.getenv('SPOTIFY_ACCESS_TOKEN')
    url = 'https://api.spotify.com/v1/me/albums'
    headers = {
        'Authorization': f'Bearer {ACCESS_TOKEN}'
    }

    albums, artists, links = [], [], []
    limit = 50
    offset = 0

    while True:
        params = {
            'limit': limit,
            'offset': offset
        }
        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            print('Failed to get liked albums', response.json())
            break

        data = response.json()
        items = data.get('items', [])
        if not items:
            break

        for item in items:
            album = item['album']
            for artist in album['artists']:
                artist_info = {
                    'id': artist['id'],
                    'name': artist['name'],
                    'href': artist['href'],
                    'uri': artist['uri']
                }
                link_info = {
                    'artist_id': artist['id'],
                    'album_id': album['id']
                }
                links.append(link_info)
                if artist_info not in artists: # improve to set()
                    artists.append(artist_info)
                    
            album_info = {
                'id': album['id'],
                'name': album['name'],
                'release_date': album['release_date'],
                'cover_url': album['images'][0]['url'] if album['images'] else None,
                'href': album['href'],
                'uri': album['uri'],
                'added_at': item['added_at']
            }
            albums.append(album_info)

        offset += limit
        if offset >= data['total']:
            break

    return albums, artists, links

def get_albums_from_database():
    conn = sqlite3.connect(LIBRARY)
    c = conn.cursor()
    c.execute('SELECT album_id FROM saved_albums')
    id_list = [item[0] for item in c.fetchall()]
    conn.close()
    return id_list

def compare_spotify_sql_albums(albums,id_list):
    sql_ids = set(id_list)
    spotify_ids = set([album['id'] for album in albums])
    new_saved_ids = spotify_ids.difference(sql_ids)
    deleted_ids = sql_ids.difference(spotify_ids)
    new_saved_albums = [next(filter(lambda x: x['id'] == '{}'.format(id), albums), None) for id in new_saved_ids]
    return new_saved_albums, list(deleted_ids)

def delete_albums(deleted_ids):
    if not deleted_ids:
        return
    conn = sqlite3.connect(LIBRARY)
    c = conn.cursor()
    deleted_ids_joined = ','.join('?' for _ in deleted_ids)
    c.execute(f'DELETE FROM saved_albums WHERE album_id IN ({deleted_ids_joined})', deleted_ids)
    c.execute(f'DELETE FROM saved_album_tracks WHERE album_id IN ({deleted_ids_joined})', deleted_ids)
    conn.commit()
    conn.close()

def get_tracks_from_album(id):
    url = 'https://api.spotify.com/v1/albums/{}/tracks'.format(id)
    headers = {
        'Authorization': f'Bearer {ACCESS_TOKEN}'
    }

    tracks, artists, links = [], [], []
    in_artists = set()
    limit = 50
    offset = 0

    while True:
        params = {
            'limit': limit,
            'offset': offset
        }
        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            print('Failed to get album tracks. Album ID:', id)
            print("Status Code:", response.status_code)
            print("Response Text:", response.text)
            return [], [], []

        data = response.json()
        items = data.get('items', [])
        if not items:
            break

        for item in items:
            for artist in item['artists']:
                link_info = {
                    'artist_id': artist['id'],
                    'song_id': item['id']
                }
                links.append(link_info)
                if artist['id'] not in in_artists:
                    artist_info = {
                        'id': artist['id'],
                        'name': artist['name'],
                        'href': artist['href'],
                        'uri': artist['uri']
                    }
                    artists.append(artist_info)
                    in_artists.add(artist['id'])
                    
            track_info = {
                'id': item['id'],
                'disc_number': item['disc_number'],
                'duration_ms': item['duration_ms'],
                'explicit': item['explicit'],
                'name': item['name'],
                'preview_url': item['preview_url'],
                'track_number': item['track_number'],
                'href': item['href'],
                'uri': item['uri'],
                'is_local': item['is_local'],
                'album_id': id
            }
            tracks.append(track_info)

        offset += limit
        if offset >= data['total']:
            break

    return tracks, artists, links

def create_album_table():
    conn = sqlite3.connect(LIBRARY)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS saved_albums (
            album_id VARCHAR(62) PRIMARY KEY,
            album_name TEXT,
            release_date TEXT,
            cover_url TEXT,
            href TEXT,
            uri TEXT,
            added_at TEXT
        )
    """)
    conn.commit()
    conn.close()
            
def save_albums_to_table(albums):
    conn = sqlite3.connect(LIBRARY)
    c = conn.cursor()

    for album in albums:
        try:
            c.execute("""
                INSERT INTO saved_albums (album_id, album_name, release_date, cover_url, href, uri, added_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (album['id'], album['name'], album['release_date'], album['cover_url'], album['href'], album['uri'], album['added_at']))
        except sqlite3.IntegrityError:
            # Album already in table, skip duplicates
            pass

    conn.commit()
    conn.close()

def create_track_table():
    conn = sqlite3.connect(LIBRARY)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS saved_album_tracks (
            song_id VARCHAR(62) PRIMARY KEY,
            song_name TEXT,
            disc_number INT,
            duration_ms INT,
            explicit BOOL,
            preview_url TEXT,
            track_number INT,
            href TEXT,
            uri TEXT,
            is_local BOOL,
            album_id VARCHAR(62)
        )
    """)
    conn.commit()
    conn.close()

def save_album_tracks_to_table(tracks):
    conn = sqlite3.connect(LIBRARY)
    c = conn.cursor()

    for track in tracks:
        try:
            c.execute("""
                INSERT INTO saved_album_tracks (song_id, song_name, disc_number, duration_ms, explicit, preview_url, track_number, href, uri, is_local, album_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (track['id'], track['name'], track['disc_number'], track['duration_ms'], track['explicit'], track['preview_url'], track['track_number'], track['href'], track['uri'], track['is_local'], track['album_id']))
        except sqlite3.IntegrityError:
            # Track already in table, skip duplicates
            pass

    conn.commit()
    conn.close()

def create_artist_table():
    conn = sqlite3.connect(LIBRARY)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS artists (
            artist_id VARCHAR(62) PRIMARY KEY,
            artist_name TEXT,
            href TEXT,
            uri TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_artists_to_table(artists):
    conn = sqlite3.connect(LIBRARY)
    c = conn.cursor()

    for artist in artists:
        try:
            c.execute("""
                INSERT INTO artists (artist_id, artist_name, href, uri)
                VALUES (?, ?, ?, ?)
            """, (artist['id'], artist['name'], artist['href'], artist['uri']))
        except sqlite3.IntegrityError:
            # Artist already in table, skip duplicates
            pass

    conn.commit()
    conn.close()

def create_artists_albums_table():
    conn = sqlite3.connect(LIBRARY)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS artists_albums (
            artist_id VARCHAR(62),
            album_id VARCHAR(62),
              
            PRIMARY KEY (artist_id, album_id),
            FOREIGN KEY (artist_id) REFERENCES artists(artist_id),
            FOREIGN KEY (album_id) REFERENCES saved_albums(album_id)
        )
    """)
    conn.commit()
    conn.close()

def save_artists_albums_to_table(links):
    conn = sqlite3.connect(LIBRARY)
    c = conn.cursor()

    for link in links:
        try:
            c.execute("""
                INSERT INTO artists_albums (artist_id, album_id)
                VALUES (?, ?)
            """, (link['artist_id'], link['album_id']))
        except sqlite3.IntegrityError:
            # Link already in table, skip duplicates
            pass

    conn.commit()
    conn.close()

def create_artists_tracks_table():
    conn = sqlite3.connect(LIBRARY)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS artists_tracks (
            artist_id VARCHAR(62),
            song_id VARCHAR(62),
              
            PRIMARY KEY (artist_id, song_id),
            FOREIGN KEY (artist_id) REFERENCES artists(artist_id),
            FOREIGN KEY (song_id) REFERENCES tracks(song_id)
        )
    """)
    conn.commit()
    conn.close()

def save_artists_tracks_to_table(links):
    conn = sqlite3.connect(LIBRARY)
    c = conn.cursor()

    for link in links:
        try:
            c.execute("""
                INSERT INTO artists_tracks (artist_id, song_id)
                VALUES (?, ?)
            """, (link['artist_id'], link['song_id']))
        except sqlite3.IntegrityError:
            # Link already in table, skip duplicates
            pass

    conn.commit()
    conn.close()


if __name__ == '__main__':
    deleted_ids = ['07h9Qsx40cCp1h0ykxuqU1', '09P40BHcaue9iF4QasXMTK']
    delete_albums(deleted_ids)
    # albums, artists, links = get_saved_albums() #[{'id':'1emkiMRnLWtWfmCcJapjR1','name':'test'},{'id':'0DQyTVcDhK9wm0f6RaErWO','name':'test2'}]
    # print(compare_spotify_sql_database(albums,get_albums_from_database()))