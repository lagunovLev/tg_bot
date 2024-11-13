from pymongo import MongoClient
import config

db_client: MongoClient = MongoClient(f'mongodb://{config.db_host}:{config.db_port}')

