import os
from spotify_oauth import app
from dotenv import load_dotenv
from get_liked_albums import (
    get_saved_albums, get_tracks_from_album, 
    create_album_table, save_albums_to_table, 
    create_track_table, save_album_tracks_to_table,
    create_artist_table, save_artists_to_table,
    create_artists_albums_table, save_artists_albums_to_table,
    create_artists_tracks_table, save_artists_tracks_to_table,
    get_albums_from_database, compare_spotify_sql_albums, delete_albums
)
from get_liked_songs import (
    get_liked_songs, create_song_table, save_songs_to_table,
    get_songs_from_database, compare_spotify_sql_songs, delete_songs
)
from dump_to_sql import dump
from config import LIBRARY, TABLE_DIR

if __name__ == '__main__':
    print('Getting Spotify authorization code...')
    app.run(port=8888)
    
    load_dotenv(override=True)
    ACCESS_TOKEN = os.getenv('SPOTIFY_ACCESS_TOKEN')

    print('Creating tables...')
    create_song_table()
    create_artist_table()
    create_album_table()
    create_artists_albums_table()
    create_track_table()
    create_artists_tracks_table()

    print('Fetching saved songs from Spotify...')
    saved_songs, artists, links = get_liked_songs(ACCESS_TOKEN)
    new_songs, removed_songs = compare_spotify_sql_songs(saved_songs, get_songs_from_database())
    print(f'Fetched {len(new_songs)} new songs.')
    if new_songs:
        print('Saving songs to table...')
        save_songs_to_table(saved_songs)
        save_artists_to_table(artists)
        save_artists_tracks_to_table(links)
    else:
        pass
    if removed_songs:
        run = True
        while run:
            exe_mode = input(f'You removed {len(removed_songs)} songs from your Spotify library. Also delete them from the database? [Y/N] ').strip().lower()
            if exe_mode == 'y':
                delete_songs(removed_songs)
                print('Successfully deleted songs not in your Spotify library.')
                run = False
            elif exe_mode =='n':
                print('No song was deleted.')
                run = False
            else:
                print('Invalid input.')


    print('Fetching saved albums from Spotify...')
    saved_albums, artists, links = get_saved_albums(ACCESS_TOKEN)
    new_albums, removed_albums = compare_spotify_sql_albums(saved_albums, get_albums_from_database())

    print(f'Fetched {len(new_albums)} new albums.')
    if new_albums:
        print('Saving albums to table...')
        save_albums_to_table(new_albums)
        save_artists_to_table(artists)
        save_artists_albums_to_table(links)

        print('Fetching tracks from saved albums...')
        all_tracks, all_links, all_artists = [], [], []
        for album in new_albums:
            id = album['id']
            tracks, artists, links = get_tracks_from_album(id)
            all_tracks += tracks
            all_links += links
            all_artists += artists
        print(f'Fetched {len(all_tracks)} new tracks.')
        
        print('Saving tracks to table...')
        save_album_tracks_to_table(all_tracks)
        save_artists_tracks_to_table(all_links)
        save_artists_to_table(all_artists)

        print('Done! Your spotify library is saved in', LIBRARY)

    if removed_albums:
        run = True
        while run:
            exe_mode = input(f'You removed {len(removed_albums)} albums from your Spotify library. Also delete them from the database? [Y/N] ').strip().lower()
            if exe_mode == 'y':
                delete_albums(removed_albums)
                print('Successfully deleted albums not in your Spotify library.')
                run = False
            elif exe_mode == 'n':
                print('No album was deleted.')
                run = False
            else:
                print('Invalid input.')

    run = True
    while run:
        exe_mode = input('Do you want to convert the library into a MySQL-compatible one (.sql)? [Y/N] ').strip().lower()
        if exe_mode == 'y':
            # exe_mode = input('Run for all .db files in the current directory? [Y/N]: ').strip().lower()
            dump(LIBRARY, f'{TABLE_DIR}spotify_library.sql')
            print('All done.')
            run = False
        elif exe_mode == 'n':
            print('All finished.')
            run = False
        else:
            print('Invalid input.')

    
