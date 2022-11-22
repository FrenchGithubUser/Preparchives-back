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

## Tableaux Enum
Matiere_enum = ['Mathematiques','Physique','Chimie','Anglais','Français-Philo']
Epreuve_enum = ['MPSI','PCSI','PTSI','MP','PC','PSI','PT']
Filiaire_enum = ['a','b','c']

## Methode pour poster un sujet
@app.route('/sujet', methods=['POST'])
@jwt_required()
def ajout_sujet():
    ## Test de la présence d'un fichier
    if 'file' in request.files:
        file = request.files['file']
    else:
        return make_response(jsonify({
            'Published' : False,
            'error' : 'Erreur lors de l\'ajout d\'un sujet : Fichier manquant'
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
            'error' : 'Erreur lors de l\'ajout d\'un sujet : Le fichier n\'est pas au format pdf'
            }),
            400)
    ## Test de la présence d'une matiere
    if 'matiere' in request.form:
        matiere = request.form["matiere"]
        if matiere in Matiere_enum:
            pass
        else:
            return make_response(jsonify({
                'Published' : False,
                'error' : 'Erreur lors de l\'ajout d\'un sujet : Matiere non conforme'
                }),
                400)
    else:
        return make_response(jsonify({
            'Published' : False,
            'error' : 'Erreur lors de l\'ajout d\'un sujet : Matiere manquante'
            }),
            400)
    ## Test de la présence d'une epreuve
    if 'epreuve' in request.form:
        epreuve = request.form["epreuve"]
        if epreuve in Epreuve_enum:
            pass
        else:
            return make_response(jsonify({
                'Published' : False,
                'error' : 'Erreur lors de l\'ajout d\'un sujet : Epreuve non conforme'
                }),
                400)
    else:
        return make_response(jsonify({
            'Published' : False,
            'error' : 'Erreur lors de l\'ajout d\'un sujet : Epreuve manquante'
            }),
            400)
     ## Test de la présence d'une filiaire
    if 'filiaire' in request.form:
        filiaire = request.form["filiaire"]
        if filiaire in Filiaire_enum:
            pass
        else:
            return make_response(jsonify({
                'Published' : False,
                'error' : 'Erreur lors de l\'ajout d\'un sujet : Filiaire non conforme'
                }),
                400)
    else:
        return make_response(jsonify({
            'Published' : False,
            'error' : 'Erreur lors de l\'ajout d\'un sujet : Filiaire manquante'
            }),
            400)
    ## Test de la présence d'un concours
    if 'concours' in request.form:
        concours = request.form["concours"]
        if len(concours)<255:
            pass
        else:
            return make_response(jsonify({
                'Published' : False,
                'error' : 'Erreur lors de l\'ajout d\'un sujet : Intiltulé du concours trop long'
                }),
                400)
    else:
        return make_response(jsonify({
            'Published' : False,
            'error' : 'Erreur lors de l\'ajout d\'un sujet : Concours manquant'
            }),
            400)
    ## Test de la présence d'une année
    if 'annee' in request.form:
        try:
            annee = int(request.form["annee"])
        except:
            return make_response(jsonify({
                'Published' : False,
                'error' : 'Erreur lors de l\'ajout d\'un sujet : L\'année n\'est pas un nombre'
                }),
                400)
    else:
        return make_response(jsonify({
            'Published' : False,
            'error' : 'Erreur lors de l\'ajout d\'un sujet : Année manquante'
            }),
            400)
    ## Test de la présence du type de concours
    if 'ecrit' in request.form:
        ecrit = int(request.form["ecrit"])
        if type(ecrit) == int and ecrit<=1 and ecrit>=0:
            pass
        else:
            return make_response(jsonify({
                'Published' : False,
                'error' : 'Erreur lors de l\'ajout d\'un sujet : Le type de concours n\'est pas conforme'
                }),
                400)
    else:
        return make_response(jsonify({
            'Published' : False,
            'error' : 'Erreur lors de l\'ajout d\'un sujet : Le type de concours est manquant'
            }),
            400)

    user_id = get_jwt_identity()

    ### Fin des test des parametres

    ## Requete SQL Insert
    try:
        params = []
        requete = "INSERT into sujet  \
                    (matiere, epreuve, filiaire, concours, annee, ecrit, id_utilisateur) \
                    VALUES(%s,%s,%s,%s,%s,%s,%s)\
                    returning id"
        params.append(matiere)
        params.append(epreuve)
        params.append(filiaire)
        params.append(concours)
        params.append(annee)
        params.append(ecrit)
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
    file.save(os.path.join(config.subject_folder + filename))
    return make_response(jsonify({
            'Published' : True,
            'filename' : filename,
            'sujet' : request.form
            }),
            200)
