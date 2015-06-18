from db import db
from sqlalchemy.event import listens_for
from datacats.environment import Environment

from os import listdir
from os.path import expanduser

class Site(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    site_name = db.Column(db.String(80), unique=True)
