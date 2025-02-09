import os
from config import secret_key, url
from flask import Flask

app = Flask(__name__)
app.config['SECRET_KEY'] = secret_key
#if os.getenv('DEPLOYING'):
#    app.config["SERVER_NAME"] = url
#else:
#    app.config["SERVER_NAME"] = "127.0.0.1:8080"
