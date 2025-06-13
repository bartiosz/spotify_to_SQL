import glob, os
from pathlib import Path
from config import TABLE_DIR
import sqlite3
from config import LIBRARY, TABLE_DIR
from dump_to_sql import dump

db_paths = glob.glob(os.path.join(os.getcwd(),f'{TABLE_DIR}*.db'))
sqlite_path = r'C:/Program Files (x86)/SQLite/'
top_line = f"USE `spotify_library`; \n"

def db_to_sql(exe_mode):
    run = True
    while run:
        if exe_mode == 'y':
            for path in db_paths:
                file_name = Path(path).with_suffix('')
                sql_file = f'{file_name}.sql'
                command = f'sqlite3.exe "{path}" .dump > "{sql_file}"'
                print(f'Running: {command}')
                os.chdir(sqlite_path)
                os.system(command)
                with open(sql_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                trim_lines = lines[2:-1] if len(lines) > 3 else []
                new_lines = [top_line] + trim_lines
                with open(sql_file, 'w', encoding='utf-8') as f:
                    f.writelines(new_lines)
                return

        elif exe_mode == 'n':
            file_input = input('Please enter the .db file name: ').strip()
            file_name = file_input if file_input.endswith('.db') else f'{file_input}.db'

            if os.path.exists(TABLE_DIR + file_name):
                cwd = Path.cwd()
                file_path = f'{cwd}/{TABLE_DIR}{file_name}'
                sql_file = f'{cwd}/{TABLE_DIR}{Path(file_name).stem}.sql'
                command = f'sqlite3.exe "{file_path}" .dump > "{sql_file}"'
                print(f'Running: {command}')
                os.chdir(sqlite_path)
                os.system(command)
                with open(sql_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                trim_lines = lines[2:-1] if len(lines) > 3 else []
                new_lines = [top_line] + trim_lines
                with open(sql_file, 'w', encoding='utf-8') as f:
                    f.writelines(new_lines)
                return
            else:
                print(f'File not found: {file_name}')
                run = input('Want to abort? [Y/N]: ').strip().lower() == 'n'

        else: 
            print('Invalid input')
            return

if __name__ == '__main__':
    dump(LIBRARY,f'{TABLE_DIR}spotify_library.sql')