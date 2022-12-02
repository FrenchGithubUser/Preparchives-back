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

    if "id_correction" in request.form:
        id_correction = request.form["id_correction"]

        if  id_correction and not sql_connector.is_correction_existing(int(id_correction)):
            return make_response(jsonify({
            'Published' : False,
            'error' : 'Erreur lors de l\'ajout d\'un commentaire : la correction commentée n\'existe pas'
            }),
            400)  

    else:
        return make_response(jsonify({
            'Published' : False,
            'error' : 'Erreur lors de l\'ajout d\'un commentaire : id_correction manquant'
            }),
            400)

    
    if "id_commentaire" in request.form:
        id_commentaire = request.form["id_commentaire"]
        if id_commentaire and not sql_connector.is_commentaire_existing(int(id_commentaire)):
            return make_response(jsonify({
            'Published' : False,
            'error' : 'Erreur lors de l\'ajout d\'un commenaitre : le commentaire commenté n\'existe pas'
            }),
            400)
    
    else:
        return make_response(jsonify({
            'Published' : False,
            'error' : 'Erreur lors de l\'ajout d\'un commentaire : id_commentaire manquant'
            }),
            400)


    if "id_sujet" in request.form:
        id_sujet = request.form["id_sujet"]
        if id_sujet and not sql_connector.is_subject_existing(int(id_sujet)):
            return make_response(jsonify({
            'Published' : False,
            'error' : 'Erreur lors de l\'ajout d\'un commentaire : le sujet commenté n\'existe pas'
            }),
            400)

    else:
        return make_response(jsonify({
            'Published' : False,
            'error' : 'Erreur lors de l\'ajout d\'un signalement : id_sujet manquant'
            }),
            400)



    # Fin des tests des paramètres
    user_id = get_jwt_identity()

    try:
        params = []

        requete = "INSERT INTO commentaire"
        params.append(content)
        params.append(user_id)

        # lié a une correction 
        if id_correction and not id_commentaire and not id_sujet:
            requete += "(contenu, id_utilisateur, id_correction) "
            params.append(id_correction)

        # lié a un commentaire
        elif not id_correction and id_commentaire and not id_sujet:
            requete += "(contenu, id_utilisateur, id_commentaire) "
            params.append(id_commentaire)

        # lié a un sujet
        elif not id_correction and not id_commentaire and id_sujet:
            requete += "(contenu, id_utilisateur, id_sujet) "
            params.append(id_sujet)

        # lié à auncun objet
        elif not id_sujet and not id_commentaire and not id_correction:
            return make_response(jsonify({
                'Published' : False,
                'error' : 'Erreur lors de l\'ajout d\'un commentaire : le commentaire n\'est lié a aucun objet'
                }),
                400)
        
        # commentaire lié a plus qu'un objet ( ne devrait pas être possible )
        else:
            return make_response(jsonify({
                'Published' : False,
                'error' : 'Erreur lors de l\'ajout d\'un commentaire : Le commentaire est lié a trop d\'objets'
                }),
                400)

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



