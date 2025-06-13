import sqlite3

conn = sqlite3.connect("spotify_library.db")
c = conn.cursor()

for row in c.execute("SELECT id, name, artists, album, duration_ms FROM liked_songs LIMIT 10"):
    print(row)

conn.close()
