import config
from database import db_client
from pymongo import collection

collect: collection = db_client[config.db_name]["categories"]


def add(name):
    collect.insert_one({"name": name})


def get_all(projection=None):
    return collect.find({}, projection)


def get_by_id(id: str):
    return collect.find_one({"_id": id})


def find_by_name(name: str):
    return collect.find_one({"name": name})


def delete_by_name(name: str):
    collect.delete_one({"name": name})
