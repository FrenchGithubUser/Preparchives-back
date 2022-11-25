from __main__ import app

import os
from flask import Flask,jsonify, request, make_response, send_file
import config
import sql_connector
import mysql.connector
import datetime
import re

from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager
from flask_jwt_extended import set_access_cookies
from flask_jwt_extended import unset_jwt_cookies

connection_params = {
        'host' : config.host_db,
        'user': config.user_db,
        'password' : config.password_db,
        'database' : config.database,
        'port' : config.port_db,
    }


## Methode pour poster un commentaire
@app.route('/commentaire', methods=['POST'])
@jwt_required()
def ajout_commentaire():

    #test présence de contenue
    if "contenu" in request.form:
        content = request.form["contenu"]
        if len(content)>1000:
            return make_response(jsonify({
            'Published' : False,
            'error' : 'Erreur lors de l\'ajout d\'un commentaire : contenu trop long (1000 caracteres max)'
            }),
            400)


    else:
        return make_response(jsonify({
            'Published' : False,
            'error' : 'Erreur lors de l\'ajout d\'un commentaire : contenu manquant'
            }),
            400)

    id_correction,id_sujet = "",""
    #test presence id_sujet
    if "id_sujet" in request.form:

        #test presence de id correction
        if "id_correction" in request.form:

            return make_response(jsonify({
            'Published' : False,
            'error' : 'Erreur lors de l\'ajout d\'un commentaire : le commentaire ne peut être lié qu\'a un sujet ou une correction'
            }),
            400)
        else:
            id_sujet = request.form["id_sujet"]

    elif "id_correction" in request.form:

        id_correction = request.form["id_correction"]

    else:
        return make_response(jsonify({
            'Published' : False,
            'error' : 'Erreur lors de l\'ajout d\'un commentaire : le commentaire doit etre lie a un sujet ou une correction'
            }),
            400)

    # Fin des tests des paramètres
    user_id = get_jwt_identity()

    try:
        params = []

        requete = "INSERT INTO commentaire"
        params.append(content)
        params.append(user_id)

        if id_correction:
            requete += "(contenu, id_utilisateur, id_correction)"
            params.append(id_correction)
        elif id_sujet:
            requete += "(contenu, id_utilisateur, id_sujet)"
            params.append(id_sujet)
        
        requete+= "VALUES (%s,%s,%s)"

        with mysql.connector.connect(**connection_params) as db :
            with db.cursor() as c:
                c.execute(requete, params)
                db.commit()

        return make_response(jsonify({
            'Published' : True,
            'commentaire' : content
            }),
            200)


    except Exception as err:
        return make_response(jsonify({
            'Published' : False,
             'error' : 'mysql_connector.Error : ' + str(err)
            }),
            500)



