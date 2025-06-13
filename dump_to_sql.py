import sqlite3
from config import LIBRARY, TABLE_DIR

def dump(db_file, sql_file):
    c = sqlite3.connect(db_file)
    with open(sql_file, 'w', encoding='utf-8') as f:
        line_number = 0
        f.write(f'SET FOREIGN_KEY_CHECKS = 0;\n')
        for line in c.iterdump():
            line1 = line.replace('CREATE TABLE', 'CREATE TABLE IF NOT EXISTS')
            new_line = line1.replace('"','')
            if line_number == 0:
                new_line = 'START TRANSACTION;'
            f.write(f'{new_line}\n')
            line_number += 1
        f.write('SET FOREIGN_KEY_CHECKS = 1;')
    c.close()
    return

if __name__ == '__main__':
    dump(LIBRARY,f'{TABLE_DIR}spotify_library.sql')