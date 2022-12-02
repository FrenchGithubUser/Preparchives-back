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

enum_type_signalement = ["insulte","contenue","autre"]

## Methode pour poster un signalement
@app.route('/signalement', methods=['POST'])
@jwt_required()
def ajout_signalement():


    #test presence d'un type de signalement
    if "type_signalement" in request.form:
        type_signalement = request.form["type_signalement"]
        if type_signalement in enum_type_signalement:
            pass
        else:
            return make_response(jsonify({
            'Published' : False,
            'error' : 'Erreur lors de l\'ajout d\'un signalement : type de signalement incorrecte'
            }),
            400)
            
    else:
        return make_response(jsonify({
            'Published' : False,
            'error' : 'Erreur lors de l\'ajout d\'un signalement : type de signalement manquant'
            }),
            400)

    # test de présence du motif
    if "motif" in request.form:
        motif = request.form["motif"]

        if len(motif)<=0:
            return make_response(jsonify({
            'Published' : False,
            'error' : 'Erreur lors de l\'ajout d\'un signalement : motif trop court'
            }),
            400)

    else:
        return make_response(jsonify({
            'Published' : False,
            'error' : 'Erreur lors de l\'ajout d\'un signalement : motif absent'
            }),
            400)

    if "id_correction" in request.form:
        id_correction = request.form["id_correction"]

        if  id_correction and not sql_connector.is_correction_existing(int(id_correction)):
            return make_response(jsonify({
            'Published' : False,
            'error' : 'Erreur lors de l\'ajout d\'un signalement : la correction signalée n\'existe pas'
            }),
            400)  

    else:
        return make_response(jsonify({
            'Published' : False,
            'error' : 'Erreur lors de l\'ajout d\'un signalement : id_utilisateur manquant'
            }),
            400)

    
    if "id_commentaire" in request.form:
        id_commentaire = request.form["id_commentaire"]
        if id_commentaire and not sql_connector.is_commentaire_existing(int(id_commentaire)):
            return make_response(jsonify({
            'Published' : False,
            'error' : 'Erreur lors de l\'ajout d\'un signalement : le commentaire signalé n\'existe pas'
            }),
            400)
    
    else:
        return make_response(jsonify({
            'Published' : False,
            'error' : 'Erreur lors de l\'ajout d\'un signalement : id_commentaire manquant'
            }),
            400)


    if "id_sujet" in request.form:
        id_sujet = request.form["id_sujet"]
        if id_sujet and  not sql_connector.is_subject_existing(int(id_sujet)):
            return make_response(jsonify({
            'Published' : False,
            'error' : 'Erreur lors de l\'ajout d\'un signalement : le sujet signalé n\'existe pas'
            }),
            400)

    else:
        return make_response(jsonify({
            'Published' : False,
            'error' : 'Erreur lors de l\'ajout d\'un signalement : id_sujet manquant'
            }),
            400)
    
    # fin récupération/tests des paramètres

    user_id = get_jwt_identity()

    try:

        params = []

        requete =  "INSERT INTO signalement "
        params.append(user_id)
        params.append(motif)
        params.append(type_signalement) 

        # lié a une correction 
        if id_correction and not id_commentaire and not id_sujet:
            requete += "(id_utilisateur, motif, type_signalement, id_correction) "
            params.append(id_correction)

        # lié a un commentaire
        elif not id_correction and  id_commentaire and not id_sujet:
            requete += "(id_utilisateur, motif, type_signalement, id_commentaire) "
            params.append(id_commentaire)

        # lié a un sujet
        elif not id_correction and not id_commentaire and id_sujet:
            requete += "(id_utilisateur, motif, type_signalement, id_sujet) "
            params.append(id_sujet)

        # Signalement lié a aucun objet 
        elif not id_sujet and not id_commentaire and not id_correction:
            return make_response(jsonify({
                'Published' : False,
                'error' : 'Erreur lors de l\'ajout d\'un signalement : le signalement n\'est lié a aucun objet'
                }),
                400)

        # signalement lié a plus qu'un objet ( ne devrait pas être possible )
        else:
            return make_response(jsonify({
                'Published' : False,
                'error' : 'Erreur lors de l\'ajout d\'un signalement : Le signalement est lié a trop d\'objets'
                }),
                400)

        requete+= "VALUES (%s,%s,%s,%s)"

        with mysql.connector.connect(**connection_params) as db :
            with db.cursor() as c:
                c.execute(requete, params)
                db.commit()

        return make_response(jsonify({
            'Published' : True,
            'Motif' : motif,
            'Type_signalement': type_signalement
            }),
            200)


    except Exception as err:
        return make_response(jsonify({
                    'Published' : False,
                    'error' : 'mysql_connector.Error : ' + str(err)
                    }),
                    500)


