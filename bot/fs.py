import gridfs
import config
from database import db_client

fs = gridfs.GridFS(db_client[config.db_name])
