import os


def delete_sqlite_file(file_name: str):
    os.remove(file_name)
