from bson.objectid import ObjectId

from bot import config
from bot.database import db_client
from pymongo import collection
from bot.database import categories

collect: collection = db_client[config.db_name]["places"]


def add(name, photos_id, description, category_name):
    collect.insert_one({"name": name,
                        "photos_id": photos_id,
                        "description": description,
                        "category_id": categories.find_by_name(category_name)["_id"]})


def update(place_id, name, photos_id, description, category_name):
    collect.replace_one({"_id": ObjectId(place_id)},
                        {"name": name,
                        "photos_id": photos_id,
                        "description": description,
                        "category_id": categories.find_by_name(category_name)["_id"]})


def get_by_id(id: str):
    return collect.find_one({"_id": ObjectId(id)})


def find_by_name(name: str):
    return collect.find_one({"name": name})


def delete_by_name(name: str):
    collect.delete_one({"name": name})


def get_all(projection=None, args=None):
    if args is None:
        args = {}
    return collect.find(args, projection)


def delete_by_id(id: str):
    collect.delete_one({"_id": ObjectId(id)})
