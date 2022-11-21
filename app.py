from crypt import methods
import os
from unittest import result
from flask import Flask,jsonify, request, make_response
from sqlalchemy import true
import config
import sql_connector
import datetime
import re
#import jwt          ##      https://www.bacancytechnology.com/blog/flask-jwt-authentication
from passlib.hash import sha256_crypt  ##      https://pythonprogramming.net/password-hashing-flask-tutorial/


## https://flask-jwt-extended.readthedocs.io/en/stable/
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager
from flask_jwt_extended import set_access_cookies
from flask_jwt_extended import unset_jwt_cookies


app = Flask(__name__)
jwt = JWTManager(app)


@app.route("/")
def index():
    return "API PREPARCHIVES"



@jwt.revoked_token_loader
@jwt.expired_token_loader
def expired_token(jwt_header, jwt_payload):
    return make_response(jsonify({
        'header': jwt_header,
        'payload' : jwt_payload,
        'error' : 'La session a expiré',
        'user' : sql_connector.get_user_info(jwt_payload["sub"])
        }),
        401)


@jwt.unauthorized_loader
@jwt.invalid_token_loader
def invalid_token(jwt_reason):
    return make_response(jsonify({
        'msg' : jwt_reason,
        'error' : "La session n'est pas valide"
        }),
        401)

app.config["JWT_COOKIE_SECURE"] = False
app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
app.config["JWT_SECRET_KEY"] = config.secret
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = datetime.timedelta(minutes=1)

app.config['JSON_AS_ASCII'] = False

if __name__ == "__main__":
    import test
    import user
    import sujet
    app.run(debug=True, port=config.port)
    




