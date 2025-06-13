#----- DEPRECATED -----

import requests
import sqlite3
from dotenv import load_dotenv
import os

from config import (
    LIBRARY
)

load_dotenv()
ACCESS_TOKEN = os.getenv('SPOTIFY_ACCESS_TOKEN')

def get_track_details(id_list):
    api_call_max = 50
    songs = []
    for i in range(0,len(id_list),api_call_max):
        ids = ','.join(id_list[i:i+api_call_max])
        url_track = f'https://api.spotify.com/v1/tracks?ids={ids}'
        url_audio = f'https://api.spotify.com/v1/audio-features?ids={ids}'
        headers = {
            'Authorization': f'Bearer {ACCESS_TOKEN}'
        }

        response_track = requests.get(url_track, headers=headers)
        response_audio = requests.get(url_audio, headers=headers)
        if response_track.status_code != 200:
            print('Failed to get tracks.')
            print('Status Code:', response_track.status_code)
            print('Response Text:', response_track.text)
            if response_track.status_code == 429:
                retry_after = response_track.headers.get('Retry-After')
                print(f'Retry after {retry_after} seconds.')
            return []
        if response_audio.status_code != 200:
            print('Failed to get tracks\' audio features.')
            print('Status Code:', response_audio.status_code)
            print('Repsponse Text:', response_audio.text)
            return []

        data_track = response_track.json()
        data_audio = response_audio.json()
        tracks = data_track.get('tracks', [])
        audios = data_audio.get('audio_features', [])
        print(audios)
        if not tracks or not audios:
            break
        for track, audio in zip(tracks, audios):
            track_info = {
                'id': track['id'],
                'popularity': track['popularity'],
                'acousticness': audio['acousticness'],
                'danceability': audio['danceability'],
                'energy': audio['energy'],
                'instrumentalness': audio['instrumentalness'],
                'key': audio['key'],
                'liveness': audio['liveness'],
                'loudness': audio['loudness'],
                'mode': audio['mode'],
                'speechiness': audio['speechiness'],
                'tempo': audio['tempo'],
                'time_signature': audio['time_signature'],
                'valence': audio['valence']
            }
            songs.append(track_info)

    return songs

def create_info_table():
    conn = sqlite3.connect(LIBRARY)
    c = conn.cursor()
    c.execute('''
              CREATE TABLE IF NOT EXSITS track_details (
                song_id VARCHAR(62) PRIMARY KEY,
                popularity INT,
                acousticness FLOAT,
                danceability FLOAT,
                energy FLOAT,
                instrumentalness FLOAT,
                key INT,
                liveness FLOAT,
                loudness FLOAT,
                mode INT,
                speechiness FLOAT,
                tempo FLOAT,
                time_signature INT,
                valence FLOAT
              )      
    ''')
    conn.commit()
    conn.close()

def save_info_table(songs):
    conn = sqlite3.connect(LIBRARY)
    c = conn.cursor()

    for song in songs:
        try:
            c.execute('''
                INSERT INTO track_details (song_id, popularity, acousticness, danceability, energy, 
                      instrumentalness, key, liveness, loudness, mode, speechiness, tempo, time_signature, valence)
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)                
            ''', (song['id'], song['popularity'], song['acousticness'], song['danceability'], song['energy'], 
                  song['instrumentalness'], song['key'], song['liveness'], song['loudness'], song['mode'], 
                  song['speechiness'], song['tempo'], song['time_signature'], song['valence']))
        except sqlite3.IntegrityError:
            # Song already in table, skip duplicates
            pass

    conn.commit()
    conn.close()
            


if __name__ == '__main__':
    print(get_track_details(['11dFghVXANMlKmJXsNCbNl']))

