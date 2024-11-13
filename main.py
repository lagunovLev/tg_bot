import os

import gridfs
from flask import Flask, render_template, redirect, url_for, request
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename

import config
from database import users, categories, places, db_client
from app import app
import api.categories

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
app_root = os.path.dirname(os.path.abspath(__file__))
fs = gridfs.GridFS(db_client[config.db_name])


class User:
    def __init__(self, username):
        self.username = username

    @staticmethod
    def is_authenticated():
        return True

    @staticmethod
    def is_active():
        return True

    @staticmethod
    def is_anonymous():
        return False

    def get_id(self):
        return self.username


@login_manager.user_loader
def user_loader(username):
    u = users.find_by_username(username)
    if not u:
        return None
    return User(username=u['name'])


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = users.find_by_username(username)
        if user and user['password'] == password:
            flask_user = User(username=user['name'])
            login_user(flask_user)
            return redirect(request.args.get("next") or url_for('admin'))
        else:
            return render_template('login.html', message="Не удалось войти")
    else:
        return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/admin')
@login_required
def admin():
    cats_iter = categories.get_all({"_id": 0})
    cat = list(cats_iter)
    l = len(cat)
    return render_template('admin.html', username=current_user.username, categorylength=l, categorylist=cat)


@app.route('/add_category', methods=['POST'])
@login_required
def add_category():
    name = request.form['name']
    categories.add(name)
    return redirect(url_for('admin'))


@app.route('/add_place', methods=['POST'])
@login_required
def add_place():
    name = request.form['name']
    description = request.form['description']
    category_name = request.form['category']
    files = request.files.getlist('photos')
    photos_id = []
    for i in files:
        contents = i.read()
        filename = secure_filename(i.filename)
        id = fs.put(contents, filename=filename)
        photos_id.append(id)
    places.add(name, photos_id, description, category_name)
    return redirect(url_for('admin'))


@app.route('/delete_category', methods=['GET'])
@login_required
def delete_category():
    name = request.args.get("name")
    categories.delete_by_name(name)
    return redirect(url_for('admin'))


if __name__ == '__main__':
    app.run()
