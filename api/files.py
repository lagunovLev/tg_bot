from flask import render_template
from app import app
from database import files
import json
from fs import fs


@app.route('/api/get-file/<name>')
def get_file(name=None):
    f = fs.get_last_version(name)
    r = app.response_class(f, direct_passthrough=True, mimetype='application/octet-stream')
    r.headers.set('Content-Disposition', 'attachment', filename=name)
    return r
