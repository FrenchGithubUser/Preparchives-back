from __main__ import app


from crypt import methods
import os
from unittest import result
from flask import Flask,jsonify, request, make_response
from sqlalchemy import true
import config
import mysql.connector
import datetime
import re
import jwt          ##      https://www.bacancytechnology.com/blog/flask-jwt-authentication
from passlib.hash import sha256_crypt  ##      https://pythonprogramming.net/password-hashing-flask-tutorial/

@app.route('/test/token', methods=['GET'])
def token():
    token = jwt.encode({'user_id' : 7,
    'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=1),
    'iat' : datetime.datetime.utcnow()}, 
    config.secret, 
    "HS256")
    response = make_response(jsonify({'token' : str(token)}), 200)
    response.set_cookie(key='x-access-token',
    value=token,
    max_age=datetime.timedelta(minutes=10))
    return response

@app.route('/test/decrypt', methods=['GET'])
def verify(*args, **kwargs):
        token = None
        if 'x-access-token' in request.cookies:
           token = request.cookies.get('x-access-token')
 
        if not token:
           return jsonify({'message': 'a valid token is missing'})
        try:
           data = jwt.decode(token, config.secret, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return make_response(jsonify('Error : La session a expiré'), 401)
        except jwt.InvalidTokenError:
            return make_response(jsonify('Error : La session est compromise'), 401)
 
        return jsonify(data)