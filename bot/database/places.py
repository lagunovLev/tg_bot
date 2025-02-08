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


def give_like(place_id, chat_id):
    # Если лайка нет:
    #   если дизлайка нет:
    #       поставить лайк
    #   иначе:
    #       поставить лайк
    #       убрать дизлайк
    # иначе:
    #   убрать лайк
    # print(place_id, chat_id)

    place = collect.find_one({"_id": ObjectId(place_id)})
    if chat_id in place["likes_users_id"]:
        collect.update_one(
            {"_id": ObjectId(place_id)},
            {
                "$inc": {"likes": -1},
                "$pull": {"likes_users_id": chat_id},
            },
            upsert=True)
    else:
        if chat_id in place["dislikes_users_id"]:
            collect.update_one(
                {"_id": ObjectId(place_id)},
                {
                    "$inc": {"dislikes": -1},
                    "$pull": {"dislikes_users_id": chat_id},
                },
                upsert=True)
        collect.update_one(
            {"_id": ObjectId(place_id)},
            {
                "$addToSet": {"likes_users_id": chat_id},
                "$inc": {"likes": 1},
            },
            upsert=True)

    # collect.update_one(
    #     {"_id": ObjectId(place_id)},
    #     {
    #         "$cond": {
    #             "if": {"likes_users_id": {"$elemMatch": {"$eq": chat_id}}},
    #             "then": {
    #                 "$inc": {"likes": -1},
    #                 "$pull": {"likes_users_id": chat_id},
    #             },
    #             "else": {
    #                 "$cond": {
    #                     "if": {"dislikes_users_id": {"$elemMatch": {"$eq": chat_id}}},
    #                     "then": {
    #                         "$inc": {"dislikes": -1},
    #                         "$pull": {"dislikes_users_id": chat_id},
    #                     },
    #                 },
    #                 "$addToSet": {"likes_users_id": chat_id},
    #                 "$inc": {"likes": 1},
    #             }
    #         },
    #     },
    #     upsert=True)


def give_dislike(place_id, chat_id):
    place = collect.find_one({"_id": ObjectId(place_id)})
    if chat_id in place["dislikes_users_id"]:
        collect.update_one(
            {"_id": ObjectId(place_id)},
            {
                "$inc": {"dislikes": -1},
                "$pull": {"dislikes_users_id": chat_id},
            },
            upsert=True)
    else:
        if chat_id in place["likes_users_id"]:
            collect.update_one(
                {"_id": ObjectId(place_id)},
                {
                    "$inc": {"likes": -1},
                    "$pull": {"likes_users_id": chat_id},
                },
                upsert=True)
        collect.update_one(
            {"_id": ObjectId(place_id)},
            {
                "$addToSet": {"dislikes_users_id": chat_id},
                "$inc": {"dislikes": 1},
            },
            upsert=True)
    #print(place_id, chat_id)
    #collect.update_one(
    #    {"_id": ObjectId(place_id)},
    #    {
    #        "$cond": {
    #            "if": {"dislikes_users_id": {"$elemMatch": {"$eq": chat_id}}},
    #            "then": {
    #                "$inc": {"dislikes": -1},
    #                "$pull": {"dislikes_users_id": chat_id},
    #            },
    #            "else": {
    #                "$cond": {
    #                    "if": {"likes_users_id": {"$elemMatch": {"$eq": chat_id}}},
    #                    "then": {
    #                        "$inc": {"likes": -1},
    #                        "$pull": {"likes_users_id": chat_id},
    #                    },
    #                },
    #                "$addToSet": {"dislikes_users_id": chat_id},
    #                "$inc": {"dislikes": 1},
    #            }
    #        },
    #    },
    #    upsert=True)


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
