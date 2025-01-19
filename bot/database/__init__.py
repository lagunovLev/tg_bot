from pymongo import MongoClient
from bot import config
db_client: MongoClient = MongoClient(f'mongodb://{config.db_host}:{config.db_port}')

#db_client: MongoClient = MongoClient(f'mongodb://localhost:27017')