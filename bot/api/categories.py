from bot.app import app
from bot.database import categories


@app.route('/api/categories', methods=['GET'])
def get_all():
    cat = categories.get_all({'_id': 0})
    return list(cat)


#@app.route('/api/categories/', methods=['GET'])
#def get_all():
#    cat = categories.get_all({'_id': 0})
#    return list(cat)
