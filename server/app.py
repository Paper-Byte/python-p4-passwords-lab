#!/usr/bin/env python3

from flask import request, session
from flask_restful import Resource

from config import app, db, api
from models import User


@app.before_request
def check_auth():
    if (not session.get('user_id')
       and request.endpoint == '/check_session'):
        return ({}, 204)


class ClearSession(Resource):

    def delete(self):

        session['page_views'] = None
        session['user_id'] = None

        return {}, 204


class Signup(Resource):

    def post(self):
        json = request.get_json()
        user = User(
            username=json['username'],
            password_hash=json['password']
        )
        db.session.add(user)
        db.session.commit()
        return user.to_dict(), 201


class CheckSession(Resource):
    def get(self):
        return ((User.query.filter_by(id=session['user_id']).first().to_dict(), 200) if session['user_id'] else ({}, 204))


class Login(Resource):
    def post(self):

        user = User.query.filter_by(
            username=(request.get_json())['username']).first()
        password = request.get_json()['password']

        if (user.authenticate(password)):
            session['user_id'] = user.id
            return user.to_dict()


class Logout(Resource):
    def delete(self):
        session['user_id'] = None
        return ({}, 204)


api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(ClearSession, '/clear', endpoint='clear')
api.add_resource(Signup, '/signup', endpoint='signup')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
