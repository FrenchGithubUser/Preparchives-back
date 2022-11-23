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
        params.append(user_id)
        params.append(id_sujet)

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
            'Correction' : request.form
            }),
            200)


## Methode pour poster une correction
@app.route('/correction/info', methods=['GET'])
@jwt_required()
def get_correction_info():

    if 'id' in request.args:
        id_correction = request.args["id"]

        if sql_connector.is_correction_existing(id_correction):
            
            correction_info = sql_connector.get_correction_info(id_correction)

            try:
                correction_info["error"]
                return make_response(jsonify({
                'Published' : False,
                'error' : 'La correction demandee n\'existe pas'
                }),
                400)

            except:
                credit = correction_info["credit"]
                utilisateur =  sql_connector.get_user_info(correction_info["id_utilisateur"])
                date_correction = correction_info["date_correction"]
                pseudo_utilisateur = utilisateur["username"]

            return make_response(jsonify({
                'credit' : credit,
                'username' : pseudo_utilisateur,
                'date_correction' : date_correction
            }))


        else:
            return make_response(jsonify({
                'error' : 'La correction demandee n\'existe pas'
                }),
                400)

    else:
        return make_response(jsonify({
                'error' : 'Erreur de chargement des informations de la correction'
                }),
                400)


@app.route('/correction/pdf', methods=['GET'])
@jwt_required()
def get_correction_pdf():
    if 'id' in request.args:
        correction_id = request.args['id']
    else:
        return make_response(jsonify({
                'error' : 'Erreur lors de l\'affichage d\'une correction: L\'identifiant n\'est pas trouvé'
                }),
                400)

    if sql_connector.is_correction_existing(correction_id):
        try:
            return send_file(path_or_file=config.correction_folder + correction_id + ".pdf")
        except:
            return make_response(jsonify({
                'error' : 'Erreur lors du chargement de la correction'
                }),
                400)
            
    else:
        return make_response(jsonify({
                'error' : 'Erreur lors de l\'affichage d\'une correction: La correction n\'existe pas'
                }),
                400)


