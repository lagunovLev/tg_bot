import json

from bot.app import app
from bot.database import places
from bson import json_util


@app.route('/api/places/', methods=['GET'], endpoint="api_places")
def get_all():
    res = places.get_all()
    return list(res)


@app.route('/api/places/names/<name>/', methods=['GET'], endpoint="api_places_names")
def get_by_name(name):
    res = places.collect.aggregate([
        {"$match": {
            "name": name,
        }},
        {"$unset": "_id"},
        {"$lookup": {
            "from": "categories",
            "localField": "category_id",
            "foreignField": "_id",
            "as": "category",
        }},
        {"$lookup": {
            "from": "fs.files",
            "localField": "photos_id",
            "foreignField": "_id",
            "as": "photos",
        }},
        {"$unset": "photos_id"},
        {"$unset": "category._id"},
        {"$unset": "category_id"},
    ])
    return json.loads(json_util.dumps(res))
