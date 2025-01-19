from flask.cli import FlaskGroup
from __init__ import *
from database import *


cli = FlaskGroup(app)


if __name__ == "__main__":
    cli()
