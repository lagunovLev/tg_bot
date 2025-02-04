from bson.objectid import ObjectId
import config
from database import db_client
from pymongo import collection
from database import categories

collect: collection = db_client[config.db_name]["places"]


def add(name, photos_id, description, category_name):
    collect.insert_one({"name": name,
                        "photos_id": photos_id,
                        "description": description,
                        "category_id": categories.find_by_name(category_name)["_id"],
                        "likes_users_id": [],
                        "dislikes_users_id": [],
                        "likes": 0,
                        "dislikes": 0})


def update(place_id, name, photos_id, description, category_name):
    collect.update_one({"_id": ObjectId(place_id)},
                       {"name": name,
                        "photos_id": photos_id,
                        "description": description,
                        "category_id": categories.find_by_name(category_name)["_id"]})


def give_like(place_id):
    collect.updateOne({"_id": ObjectId(place_id)}, {"$inc": {"likes": 1}})


def give_dislike(place_id):
    collect.updateOne({"_id": ObjectId(place_id)}, {"$inc": {"dislikes": 1}})


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
