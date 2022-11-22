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
Filiere_enum = ['MPSI','PCSI','PTSI','MP','PC','PSI','PT']
Epreuve_enum = ['a','b','c']

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
     ## Test de la présence d'une filiere
    if 'filiere' in request.form:
        filiere = request.form["filiere"]
        if filiere in Filiere_enum:
            pass
        else:
            return make_response(jsonify({
                'Published' : False,
                'error' : 'Erreur lors de l\'ajout d\'un sujet : filiere non conforme'
                }),
                400)
    else:
        return make_response(jsonify({
            'Published' : False,
            'error' : 'Erreur lors de l\'ajout d\'un sujet : filiere manquante'
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
                    (matiere, epreuve, filiere, concours, annee, ecrit, id_utilisateur) \
                    VALUES(%s,%s,%s,%s,%s,%s,%s)\
                    returning id"
        params.append(matiere)
        params.append(epreuve)
        params.append(filiere)
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



@app.route('/sujet/search', methods=['GET'])
@jwt_required()
def search_sujet():
    requete = 'SELECT * FROM sujet'
    params = []
    if len(request.args)== 0:
        pass
    else:
        requete = requete + ' where '

    ## gestion du parametre matiere
    if 'matiere' in request.args:
        matiere = request.args['matiere']
        if matiere in Matiere_enum:
            requete = requete + ' matiere = %s '
            params.append(matiere)
        else:
            return make_response(jsonify({
                'Published' : False,
                'error' : 'Erreur lors de la recherche d\'un sujet : Matiere non conforme'
                }),
                400)

    ## Gestion du parametre filiere
    if 'filiere' in request.args:
        filiere = request.args['filiere']
        if filiere in Filiere_enum:
            if len(request.args) ==  1:
                requete = requete + ' filiere = %s '
            else:
                if 'matiere' in request.args:
                    requete = requete + ' and filiere = %s '
                else:
                    requete = requete + ' filiere = %s '
            params.append(filiere)
        else:
            return make_response(jsonify({
                'Published' : False,
                'error' : 'Erreur lors de la recherche d\'un sujet : Filiere non conforme'
                }),
                400)

    ## Gestion parametre epreuve
    if 'epreuve' in request.args:
        epreuve = request.args['epreuve']
        if epreuve in Epreuve_enum:
            if len(request.args) ==  1:
                requete = requete + ' epreuve = %s '
            else:
                if 'matiere' in request.args or 'filiere' in request.args:
                    requete = requete + ' and epreuve = %s '
                else:
                    requete = requete + ' epreuve = %s '
            params.append(epreuve)
        else:
            return make_response(jsonify({
                'Published' : False,
                'error' : 'Erreur lors de la recherche d\'un sujet : Epreuve non conforme'
                }),
                400)

     ## Gestion parametre epreuve
    if 'annee' in request.args:
        try:
            annee = int(request.args["annee"])
        except:
            return make_response(jsonify({
                'Published' : False,
                'error' : 'Erreur lors de la recherche d\'un sujet : L\'année n\'est pas un nombre'
                }),
                400)

        if len(request.args) ==  1:
            requete = requete + ' annee = %s '
        else:
            if 'matiere' in request.args or 'filiere' in request.args or 'epreuve' in request.args:
                requete = requete + ' and annee = %s '
            else:
                requete = requete + ' annee = %s '
        params.append(annee)
        
     ## Gestion parametre ecrit
    if 'ecrit' in request.args:
        ecrit = int(request.args["ecrit"])
        if type(ecrit) == int and ecrit<=1 and ecrit>=0:
            if len(request.args) ==  1:
                requete = requete + ' ecrit = %s '
            else:
                if 'matiere' in request.args or 'filiere' in request.args or 'epreuve' in request.args or 'annee' in request.args:
                    requete = requete + ' and ecrit = %s '
                else:
                    requete = requete + ' ecrit = %s '
            params.append(ecrit)
        else:
            return make_response(jsonify({
                'Published' : False,
                'error' : 'Erreur lors de l\'ajout d\'un sujet : Le type de concours n\'est pas conforme'
                }),
                400)
    try:
        with mysql.connector.connect(**connection_params) as db :
            with db.cursor() as c:
                c.execute(requete, params)
                results =  c.fetchall()

    except Exception as err:
        return make_response(jsonify({
            'Published' : False,
             'error' : 'mysql_connector.Error : ' + str(err)
            }),
            500)
    nb_results = len(results)
    pretty_result = []
    for i in range (0,nb_results):
        result_dictionnary = {}
        result_dictionnary['id'] = results[i][0]
        result_dictionnary['matiere'] = results[i][1]
        result_dictionnary['filiere'] = results[i][2]
        result_dictionnary['epreuve'] = results[i][3]
        result_dictionnary['concours'] = results[i][4]
        result_dictionnary['ecrit'] = results[i][5]
        result_dictionnary['date_ajout'] = results[i][6]
        result_dictionnary['id_utilisateur'] = results[i][7]
        pretty_result.append(result_dictionnary)
    

    return make_response(
        jsonify(pretty_result),
        200)
