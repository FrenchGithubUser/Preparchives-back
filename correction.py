from __main__ import app

import os
from flask import Flask,jsonify, request, make_response
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


## Methode pour poster un sujet
@app.route('/correction', methods=['POST'])
@jwt_required()
def ajout_correction():

    user_id = get_jwt_identity()

    ## Test de la présence d'un fichier
    if 'file' in request.files:
        file = request.files['file']
    else:
        return make_response(jsonify({
            'Published' : False,
            'error' : 'Erreur lors de l\'ajout d\'une correction : Fichier manquant'
            }),
            400)
    ##Test pour savoir si le fichier a l'extension pdf
    pattern = "^\S+\.pdf+$"
    objs = re.search(pattern, file.filename)
    try:
        if objs.string == file.filename:
            pass
    except:
        return make_response(jsonify({
            'Published' : False,
            'error' : 'Erreur lors de l\'ajout d\'une correction : Le fichier n\'est pas au format pdf'
            }),
            400)

    ## Test de la présence de credit
    if 'credit' in request.form:
        credit = request.form["credit"]
        if len(credit)>255:
            return make_response(jsonify({
                'Published' : False,
                'error' : 'Erreur lors de l\'ajout d\'une correction : Crédit trop long'
                }),
                400)

    else:
        user = sql_connector.get_user_info(user_id)
        credit = user["username"]

    ## Test de la présence d'un sujet
    if 'id_sujet' in request.form:
        id_sujet = request.form["id_sujet"]

        if not sql_connector.is_subject_existing(id_sujet):
            return make_response(jsonify({
            'Published' : False,
            'error' : 'Erreur lors de l\'ajout d\'une correction : Le sujet lié n\'existe pas'
            }),
            400)

    else:
        return make_response(jsonify({
            'Published' : False,
            'error' : 'Erreur lors de l\'ajout d\'une correction : La correction n\'est lié à aucun sujet'
            }),
            400)

    ### Fin des test des parametres
    user_id = get_jwt_identity()
    ## Requete SQL Insert
    try:
        params = []
        requete = "INSERT into correction  \
                    (credit, id_utilisateur, id_sujet) \
                    VALUES(%s,%s,%s)\
                    returning id"
        params.append(credit)
        params.append(id_sujet)
        params.append(user_id)

        with mysql.connector.connect(**connection_params) as db :
            with db.cursor() as c:
                c.execute(requete, params)
                id = c.fetchone()[0]
                db.commit()
    except Exception as err:
        return make_response(jsonify({
            'Published' : False,
             'error' : 'mysql_connector.Error : ' + str(err)
            }),
            500)

    ## Ajout du fichier dans le dossier
    filename = str(id) + ".pdf"
    file.save(os.path.join(config.correction_folder + filename))
    return make_response(jsonify({
            'Published' : True,
            'filename' : filename,
            'sujet' : request.form
            }),
            200)