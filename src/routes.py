#! /usr/bin/env python
# -*- coding: utf-8 -*-

import json
from json import dumps as collect, loads as parse
from src import app, db
from flask import request
from src.models import Users, Boards


@app.route('/')
def api_home():
    return 'OK', 200


@app.route('/auth/login', methods=['GET'])
def auth_login(**args):
    login = request.args.get('login') if request else args.get('login')
    password = request.args.get('password') if request else args.get(
        'password')
    user = Users.query.filter((Users.phone == "+" + login[1:]) | (Users.email == login),
                              Users.password == password).first()

    if user is not None:
        user.update_key()
        return json.dumps({
            "user": user.object(),
            "key": user.key,
        })

    return 'Неверные данные', 404


@app.route('/user', methods=['GET', 'POST', 'PATCH'])
def profile():
    if request.method == 'GET':
        key = request.args.get('key')
        user = Users.query.filter(Users.key == key).first()
        if user is not None:
            return json.dumps(user.object())
        else:
            return 'Unauthorized', 401

    if request.method == 'POST':
        email = request.args.get('email')
        phone = request.args.get('phone')
        password = request.args.get('password')
        password_confirmation = request.args.get('password_confirmation')
        if password == password_confirmation:
            user = Users(email=email, phone=phone, password=password)
            user.update_key()
            db.session.add(user)
            db.session.commit()
            return json.dumps({
                "user": user.object(),
                "key": user.key,
            })
        else:
            return 'Password dont match', 400
    if request.method == 'PATCH':
        key = request.args.get('key')
        email = request.args.get('email')
        phone = request.args.get('phone')
        password = request.args.get('password')
        password_confirmation = request.args.get('password_confirmation')
        user = Users.query.filter(Users.key == key).first()
        if user:
            if email or phone:
                user.update(email=email, phone=phone)
            if password:
                if password == password_confirmation:
                    user.update(password=password)
                else:
                    return 'Password dont match', 400
            return json.dumps(user.object()), 200
        else:
            return 'Unauthorized', 401


@app.route('/boards', methods=['GET'])
def available_boards():
    key = request.args.get('key')
    user = Users.query.filter(Users.key == key).first()
    if user:
        if request.method == 'GET':
            return json.dumps([board.object() for board in Boards.query.all() if user.id in board.members])
        else:
            return 'Bad request method', 405
    else:
        return 'Access denied', 401


@app.route('/board', methods=['POST'])
def create_board(): # -> str | tuple:
    key = request.json.get('key')
    user = Users.query.filter(Users.key == key).first()
    if user:
        if request.method == 'POST':
            name = request.json.get('name')
            board = Boards(name=name, members=[user.id])
            db.session.add(board)
            db.session.commit()
            return json.dumps(board.object())
        else:
            return 'Bad request method', 405
    else:
        return 'Access denied', 401


@app.route('/board/<board_id>', methods=['GET', 'PATCH'])
def board_by_id(board_id): # -> str | tuple:
    key = request.args.get('key')
    user = Users.query.filter(Users.key == key).first()

    if user:
        if request.method == 'GET':
            board = Boards.query.filter_by(id=board_id).first()
            if not board:
                return 'Board access denied', 403
            return json.dumps(board.object())
        elif request.method == 'PATCH':
            name = request.args.get('name')
            board = Boards.query.filter_by(id=board_id).first()
            if board:
                board.update(name=name)
                return json.dumps(board.object())
            else:
                return 'Board not found', 404
        else:
            return 'Bad request method', 405
    else:
        return 'Access denied', 401


@app.route('/board/<board_id>/members', methods=['PUT', 'DELETE'])
def add_member(board_id):
    key = request.args.get('key')
    user = Users.query.filter(Users.key == key).first()

    if user:
        if request.method == 'PUT':
            members = request.args.get('members')
            board = Boards.query.filter_by(id=board_id).first()
            if board:
                board.members = board.members + members
                return json.dumps(board.object())
            else:
                return 'Board not found', 404
        elif request.method == 'DELETE':
            members = request.args.get('members')
            board = Boards.query.filter_by(id=board_id).first()
            if board:
                [board.members.remove(x) for x in members]
                return json.dumps(board.object())
            else:
                return 'Board not found', 404
        else:
            return 'Bad request method', 405
    else:
        return 'Access denied', 401


@app.route('/board/<board_id>/cards', methods=['POST'])
def add_card(board_id):
    key = request.args.get('key')
    user = Users.query.filter(Users.key == key).first()
    if user:
        if request.method == 'POST':
            board = request.args.get('board')
            name = request.args.get('name')
            description = request.args.get('description')
            checklist = request.args.get('checklist')
        else:
            return 'Bad request method', 405
    else:
        return 'Access denied', 401


# [print(user) for user in Users.query.all()]
