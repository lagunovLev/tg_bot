import config
from database import db_client
from pymongo import collection
from database import categories

collect: collection = db_client[config.db_name]["places"]


def add(name, photos_id, description, category_name):
    collect.insert_one({"name": name,
                        "photos_id": photos_id,
                        "description": description,
                        "category_id": categories.find_by_name(category_name)["_id"]})



