from crypt import methods
import os
from unittest import result
from flask import Flask,jsonify, request, make_response
from sqlalchemy import true
import config
import sql_connector
from datetime import datetime, timezone, timedelta
from flask_cors import CORS
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
## Fonction permettant de gérer une session avec un token expiré
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
## Fonction permettant de gerer un requete avec un utilisateur non connecté
def invalid_token(jwt_reason):
    return make_response(jsonify({
        'msg' : jwt_reason,
        'error' : "Vous n'etes pas connecté"
        }),
        401)


## Gestion de erreur 404 / endpoint non trouvé
@app.errorhandler(404)
def not_found(e):
    return make_response(jsonify({
        'msg' : str(e),
        'error' : "Endpoint invalide"
        }),
        404)

## Fonction pour refresh le token jwt apres chaque requete si le token de base expire dans moins de 60min
@app.after_request
def refresh_expiring_jwts(response):
    try:
        exp_timestamp = get_jwt()["exp"]
        now = datetime.now(timezone.utc)
        target_timestamp = datetime.timestamp(now + timedelta(minutes=60))
        if target_timestamp > exp_timestamp:
            access_token = create_access_token(identity=get_jwt_identity())
            set_access_cookies(response, access_token)
        return response
    except (RuntimeError, KeyError):
        # Case where there is not a valid JWT. Just return the original response
        return response

## Config
app.config["JWT_COOKIE_SECURE"] = False             
app.config["JWT_TOKEN_LOCATION"] = ["cookies"]      ## Enregistrement du token de session dans les cookies
app.config["JWT_SECRET_KEY"] = config.secret        ## Clé privée permettant de générer les token
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=120)     ## Durée de vie du token
app.config["JWT_COOKIE_CSRF_PROTECT"] = False

app.config['JSON_AS_ASCII'] = False                 ## Permet d'utiliser les accents et caractères UTF-8 dans les reponse JSON

cors = CORS(app, resources={r"/*": {"origins": "*"}})

if __name__ == "__main__":
    import test
    import user
    import sujet
    import correction
    import commentaire
    app.run(debug=True, port=config.port, host='0.0.0.0')
    





