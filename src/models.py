#! /usr/bin/env python
# -*- coding: utf-8 -*-

import random
import string

from src import db


class Users(db.Model):
    id = db.Column(db.INT, autoincrement=True, primary_key=True)
    email = db.Column(db.String(64), unique=True, nullable=True)
    phone = db.Column(db.String(64), unique=True, nullable=True)
    password = db.Column(db.String(64), nullable=True)
    key = db.Column(db.String(24), unique=True, nullable=True)

    def update(self, **data):
        if 'email' in data and data.get('email') is not None:
            self.email = data.get('email')
        if 'phone' in data and data.get('phone') is not None:
            self.phone = data.get('phone')
        if 'password' in data and data.get('password') is not None:
            self.password = data.get('password')
        print(self.email, self.object())
        db.session.commit()

    def update_key(self):
        self.key = ''.join(random.sample(string.ascii_letters + string.digits, 24))
        db.session.commit()

    def __repr__(self):
        return f"User:{self.id}, Email({self.email}), Phone({self.phone}), Password({self.password})"

    def object(self):
        return {
            "id": self.id,
            "email": self.email,
            "phone": self.phone,
        }


class Boards(db.Model):
    id = db.Column(db.INT, autoincrement=True, primary_key=True)
    name = db.Column(db.String(64), unique=False, nullable=True)
    members = db.Column(db.JSON, default=lambda: [])
    cards = db.Column(db.JSON, default=lambda: [])

    def update(self, **data):
        if 'name' in data and data.get('name') is not None:
            self.name = data.get('name')
            print(self.name, self.object())
            db.session.commit()

    def object(self):
        return {
            "id": self.id,
            "name": self.name,
            "members": [Users.query.filter_by(id=member).first().object() for member in self.members],
            "cards": [Cards.query.filter_by(id=card).first().object() for card in self.cards],
        }

    def __repr__(self):
        return f"Board({self.id}) {self.name}"


class Cards(db.Model):
    id = db.Column(db.INT, autoincrement=True, primary_key=True)
    board = db.Column(db.INT, db.ForeignKey('boards.id'))
    name = db.Column(db.String(64), unique=False, nullable=True)
    description = db.Column(db.String(2048), unique=False, nullable=True)
    checklist = db.Column(db.JSON, nullable=True, default=lambda: [])
    members = db.Column(db.JSON, default=lambda: [])
    start_date = db.Column(db.String(20), nullable=True)
    end_date = db.Column(db.String(20), nullable=True)

    def object(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "checklist": self.checklist,
            "members": [Users.query.filter_by(id=m).first().object() for m in self.members],
            "start_date": self.start_date,
            "end_date": self.end_date,
        }

    def __repr__(self):
        return f"Card({self.id} - {Boards.query.filter_by(id=self.id).first().name}) {self.name} | {self.checklist}"


db.create_all()
