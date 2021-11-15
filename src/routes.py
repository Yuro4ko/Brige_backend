#! /usr/bin/env python
# -*- coding: utf-8 -*-

import json
from json import dumps as collect, loads as parse
from src import app, db
from flask import request
from src.models import Users, Boards, Cards


@app.route('/')
def api_home():
    return 'OK', 200


@app.route('/auth/login', methods=['GET'])  # Authorization using login(phone or email) and password
def auth_login(**args):
    if request.method == 'GET':
        login = request.args.get('login') if request else args.get('login')
        password = request.args.get('password') if request else args.get('password')
        user = Users.query.filter((Users.phone == "+" + login[1:]) | (Users.email == login),
                                  Users.password == password).first()  # Database comparison
        if user is not None:
            user.update_key()
            return json.dumps({  # Return user to front-end
                "user": user.object(),
                "key": user.key,
            })
        else:
            return 'Unauthorized', 401  # if user not found
    else:
        return 'Bad request method', 405  # if request method isn't GET


@app.route('/user', methods=['GET', 'POST', 'PATCH'])
def profile():
    if request.method == 'GET':  # Getting data about the current user
        key = request.args.get('key')
        user = Users.query.filter(Users.key == key).first()  # Take the first user by the access key
        if user is not None:
            return json.dumps(user.object())
        else:
            return 'Unauthorized', 401

    elif request.method == 'POST':  # Registration new user
        email = request.args.get('email')
        phone = request.args.get('phone')
        password = request.args.get('password')
        password_confirmation = request.args.get('password_confirmation')
        if password == password_confirmation:  # Password check
            user = Users(email=email, phone=phone, password=password)
            user.update_key()
            db.session.add(user)  # Add data to database
            db.session.commit()
            return json.dumps({
                "user": user.object(),
                "key": user.key,
            })
        else:
            return 'Password dont match', 400
    elif request.method == 'PATCH':  # Change information about user
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
    else:
        return 'Bad request method', 405


@app.route('/boards', methods=['GET'])  # Get board by id
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


@app.route('/board', methods=['POST'])  # Create board
def create_board():
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


@app.route('/board/<board_id>', methods=['GET', 'PATCH'])  # Get board by id and chage it
def board_by_id(board_id):
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


@app.route('/board/<board_id>/members', methods=['PUT', 'DELETE'])  # Add and delete members from the board
def change_board_members(board_id):
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
                [board.members.remove(x) for x in members]  # Remove duplicate items in lists
                return json.dumps(board.object())
            else:
                return 'Board not found', 404
        else:
            return 'Bad request method', 405
    else:
        return 'Access denied', 401


@app.route('/board/<board_id>/cards', methods=['POST'])  # Create card
def add_card(board_id):
    key = request.json.get('key')
    user = Users.query.filter(Users.key == key).first()
    if user:
        if request.method == 'POST':
            name = request.json.get('name')
            card = Cards(name=name, board=board_id)
            db.session.add(card)
            db.session.commit()
            return json.dumps(card.object())
        else:
            return 'Bad request method', 405
    else:
        return 'Access denied', 401


@app.route('/board/<board_id>/cards/<card_id>', methods=['PATCH'])  # Change card information
def change_card(board_id, card_id):
    key = request.args.get('key')
    user = Users.query.filter(Users.key == key).first()
    if user:
        if request.method == 'PATCH':
            card = Cards.query.filter(Cards.id == card_id).first()
            card.index = request.args.get('index')
            card.card.name = request.args.get('name')
            card.description = request.args.get('description')
            card.checklist = request.args.get('checklist')
            card.start_date = request.args.get('start_date')
            card.end_date = request.args.get('end_date')
            db.session.commit()
            return json.dumps(card.object())
        else:
            return 'Bad request method', 405
    else:
        return 'Access denied', 401


@app.route('/board/<board_id>/cards/<card_id>/members', methods=['PUT', 'DELETE'])  # Add and delete members from card
def change_card_members(board_id, card_id):
    key = request.args.get('key')
    user = Users.query.filter(Users.key == key).first()
    if user:
        if request.method == 'PUT':
            card = Cards.query.filter(Cards.id == card_id).first()
            members = request.args.get('members')
            if card:
                card.members = card.members + members
                return json.dumps(card.object())
            else:
                return 'Card not found', 404
        elif request.method == 'DELETE':
            card = Cards.query.filter(Cards.id == card_id).first()
            members = request.args.get('members')
            if card:
                [card.members.remove(x) for x in members]
                return json.dumps(card.object())
            else:
                return 'Card not found', 404
        else:
            return 'Bad request method', 405
    else:
        return 'Access denied', 401


# [print(user) for user in Users.query.all()]
