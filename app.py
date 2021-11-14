import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///brige.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Users(db.Model):
    id = db.Column(db.INT, primary_key=True, autoincrement=True)
    email = db.Column(db.String(64))
    password = db.Column(db.String(64))
    phone = db.Column(db.String(64))
    token = db.Column(db.String(24))

    def json(self):
        return {"id": self.id, "email": self.email, "password": self.password, "phone": self.phone, "token": self.token}


db.create_all()

print(Users.query.filter_by(id = 1).all())