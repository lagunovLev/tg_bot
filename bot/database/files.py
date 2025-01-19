import gridfs
from bot import config
from bot.database import db_client

fs = gridfs.GridFS(db_client[config.db_name])


def get_file_binary(id: str):
    with open(fs.get(id), 'rb') as file:
        return file.read()
