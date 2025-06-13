import requests
import sqlite3
from dotenv import load_dotenv
import os

from config import (
    LIBRARY
)


def get_liked_songs(ACCESS_TOKEN):
    # load_dotenv()
    # ACCESS_TOKEN = os.getenv('SPOTIFY_ACCESS_TOKEN')
    url = "https://api.spotify.com/v1/me/tracks"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }

    songs, artists, links = [], [], []
    in_artists = set()
    limit = 50
    offset = 0

    while True:
        params = {
            "limit": limit,
            "offset": offset
        }
        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            print("Failed to get liked songs:", response.json())
            break

        data = response.json()
        items = data.get("items", [])
        if not items:
            break

        for item in items:
            track = item["track"]
            for artist in track['artists']:
                link_info = {
                    'artist_id': artist['id'],
                    'song_id': track['id']
                }
                links.append(link_info)
                if artist['id'] not in in_artists:
                    artist_info = {
                        'id': artist['id'],
                        'name': artist['name'],
                        'href': artist['href'],
                        'uri': artist['uri'],
                    }
                    artists.append(artist_info)
                    in_artists.add(artist['id'])
                    
            song_info = {
                "id": track["id"],
                'disc_number': track['disc_number'],
                "duration_ms": track["duration_ms"],
                'explicit': track['explicit'],
                "name": track["name"],
                'preview_url': track['preview_url'],
                'track_number': track['track_number'],
                'href': track['href'],
                'uri': track['uri'],
                'is_local': track['is_local'],
                'album_id': track['album']['id'],
                "popularity": track["popularity"],      # not in get_album_tracks
                "added_at": item["added_at"]            # not in get_album_tracks
            }
            songs.append(song_info)

        offset += limit
        if offset >= data["total"]:
            break

    return songs, artists, links

def get_songs_from_database():
    conn = sqlite3.connect(LIBRARY)
    c = conn.cursor()
    c.execute('SELECT song_id FROM saved_songs')
    id_list = [item[0] for item in c.fetchall()]
    conn.close()
    return id_list

def compare_spotify_sql_songs(songs,id_list):
    sql_ids = set(id_list)
    spotify_ids = set([song['id'] for song in songs])
    new_saved_ids = spotify_ids.difference(sql_ids)
    deleted_ids = sql_ids.difference(spotify_ids)
    new_saved_songs = [next(filter(lambda x: x['id'] == '{}'.format(id), songs), None) for id in new_saved_ids]
    return new_saved_songs, list(deleted_ids)

def delete_songs(deleted_ids):
    if not deleted_ids:
        return
    deleted_ids_joined = ','.join('?' for _ in deleted_ids)
    conn = sqlite3.connect(LIBRARY)
    c = conn.cursor()
    c.execute(f'DELETE FROM saved_songs WHERE song_id in ({deleted_ids_joined})', deleted_ids)
    conn.commit()
    conn.close()

def create_song_table():
    conn = sqlite3.connect(LIBRARY)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS saved_songs (
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
            album_id VARCHAR(62),
            popularity INT,
            added_at TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_songs_to_table(songs):
    conn = sqlite3.connect(LIBRARY)
    c = conn.cursor()

    for song in songs:
        try:
            c.execute("""
                INSERT INTO saved_songs (song_id, song_name, disc_number, duration_ms, explicit, preview_url, track_number, href, uri, is_local, album_id, popularity, added_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (song['id'], song['name'], song['disc_number'], song['duration_ms'], song['explicit'], song['preview_url'], song['track_number'], song['href'], song['uri'], song['is_local'], song['album_id'], song['popularity'], song['added_at']))
        except sqlite3.IntegrityError:
            # Song already in DB, skip duplicates
            pass

    conn.commit()
    conn.close()

