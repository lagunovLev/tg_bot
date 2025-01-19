from config import secret_key
from flask import Flask

app = Flask(__name__)
app.config['SECRET_KEY'] = secret_key

