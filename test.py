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


## https://flask-jwt-extended.readthedocs.io/en/stable/
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager
from flask_jwt_extended import set_access_cookies
from flask_jwt_extended import unset_jwt_cookies






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




@app.route("/test/protected")
@jwt_required()
def protected():
    claims = get_jwt()
    return jsonify(claims)


# @app.after_request
# def refresh_expiring_jwts(response):
#     try:
#         exp_timestamp = get_jwt()["exp"]
#         now = datetime.datetime.now(datetime.timezone.utc)
#         target_timestamp = datetime.datetime.timestamp(now+ datetime.timedelta(minutes=30))
#         if target_timestamp > exp_timestamp:
#             access_token = create_access_token(identity=get_jwt_identity())
#             set_access_cookies(response, access_token)
#         return response
#     except (RuntimeError, KeyError):
#         # Case where there is not a valid JWT. Just return the original response
#         return response


@app.route("/test/login", methods=["GET"])
def login_():
    response = jsonify({"msg": "login successful"})
    additional_claims = {"aud": "some_audience", "foo": "bar"}
    access_token = create_access_token(identity=7, additional_claims=additional_claims)
    set_access_cookies(response, access_token)
    return response


@app.route("/test/logout", methods=["GET"])
def logout_():
    response = jsonify({"msg": "logout successful"})
    unset_jwt_cookies(response)
    return response


@app.route("/test/refresh", methods=["GET"])
@jwt_required(refresh=True)
def refresh():
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)
    response = jsonify({"msg": "refresh successful"})
    set_access_cookies(response, access_token)
    return response

