from pymongo import MongoClient
import config

db_client: MongoClient = MongoClient(f'{config.db_host}')  # :{config.db_port}

