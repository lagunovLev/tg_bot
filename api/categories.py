from app import app
from database import categories
import json


@app.route('/api/categories', methods=['GET'])
def get_all():
    cat = categories.get_all({'_id': 0})
    return list(cat)


#@app.route('/api/categories/', methods=['GET'])
#def get_all():
#    cat = categories.get_all({'_id': 0})
#    return list(cat)
