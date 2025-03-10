from bot import config
from bot.database import db_client
from pymongo import collection

collect: collection = db_client[config.db_name]["users"]


def find_by_username(username: str):
    return collect.find_one({"name": username})


def get_all():
    return collect.find({})


def change_field_in_user(username: str, key, value):
    if collect.find_one({"name": username}) is not None:
        collect.update_one({"name": username}, {"$set": {key: value}})


def get_by_id(user_id: str):
    return collect.find_one({"_id": user_id})
