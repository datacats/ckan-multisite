from db import db

class Site(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    site_name = db.Column(db.String(80), unique=True)
