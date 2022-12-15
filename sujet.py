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

## Tableaux Enum
Matiere_enum = ['Mathematiques', 'Physique','Chimie', 'Anglais', 'Français-Philo','SI','Informatique', 'Biologie']
Filiere_enum = ['TSI','BCPST', 'MP','PC', 'PSI','PT']
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
    # pattern = "^\S+\.pdf+$"
    # objs = re.search(pattern, file.filename)
    # try:
    #     if objs.string == file.filename:
    #         pass
    # except:
    #     return make_response(jsonify({
    #         'Published' : False,
    #         'error' : 'Erreur lors de l\'ajout d\'un sujet : Le fichier n\'est pas au format pdf'
    #         }),
    #         400)
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
def search_sujet():
    requete = 'SELECT * FROM sujet'
    params = []

    ## gestion du parametre matiere
    if 'matiere' in request.args:
        matiere = request.args['matiere']

        if matiere == "":
            pass
        else:
            if matiere in Matiere_enum:
                requete = requete + ' where matiere = %s '
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

        if not filiere:
            pass

        else:
            if filiere in Filiere_enum:
                if not matiere:
                    requete = requete + ' where filiere = %s '
                else:
                    requete = requete + ' and filiere = %s '
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
        if not epreuve:
            pass

        else:
            if epreuve in Epreuve_enum:
                if not matiere and not filiere:
                    requete = requete + ' where epreuve = %s '
                else:
                    requete = requete + ' and epreuve = %s '
                params.append(epreuve)
            else:
                return make_response(jsonify({
                    'Published' : False,
                    'error' : 'Erreur lors de la recherche d\'un sujet : Epreuve non conforme'
                    }),
                    400)

     ## Gestion parametre epreuve
    if 'annee' in request.args:
        
        annee = request.args["annee"]

        if not annee:
            pass
        else:
            try:
                annee = int(request.args["annee"])
            except:
                return make_response(jsonify({
                    'Published' : False,
                    'error' : 'Erreur lors de la recherche d\'un sujet : L\'année n\'est pas un nombre'
                    }),
                    400)

            if not matiere and not filiere and not epreuve:
                requete = requete + ' where annee = %s '
            else:
                requete = requete + ' and annee = %s '
                
            params.append(annee)
        
     ## Gestion parametre ecrit
    if 'ecrit' in request.args:

        ecrit = request.args["ecrit"]

        if not ecrit:
            pass

        else:
            ecrit = int(ecrit)

            if type(ecrit) == int and ecrit<=1 and ecrit>=0:

                if not matiere and not filiere and not epreuve and not annee:
                    requete = requete + ' where ecrit = %s '
                else:
                        requete = requete + ' and ecrit = %s '
                params.append(ecrit)

            else:
                return make_response(jsonify({
                'Published' : False,
                'error' : 'Erreur lors de l\'ajout d\'un sujet : Le type de concours n\'est pas conforme'
                }),
                400)


    else:
        return make_response(jsonify({
            'Published' : False,
            'error' : 'Erreur lors de l\'ajout d\'un sujet : Le type de concours n\'est pas présent (écrit ou oral)'
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
    # traitement des résultats de recherche
    for i in range (0,nb_results):

        print (results)

        result_dictionnary = {}
        result_dictionnary['id'] = results[i][0]
        result_dictionnary['matiere'] = results[i][1]
        result_dictionnary['filiere'] = results[i][2]
        result_dictionnary['epreuve'] = results[i][3]
        result_dictionnary['concours'] = results[i][4]
        result_dictionnary['annee'] = results[i][5]
        result_dictionnary['ecrit'] = results[i][6]
        result_dictionnary['date_ajout'] = results[i][7]
        result_dictionnary['id_utilisateur'] = results[i][8]
        result_dictionnary['has_correction'] = results[i][9]    

        pretty_result.append(result_dictionnary)

    # renvoie l'ensemble des résultats de la recherche
    return make_response(
        jsonify(pretty_result),
        200)


@app.route('/sujet/pdf', methods=['GET'])
def get_sujet_pdf():
    if 'id' in request.args:
        sujet_id = request.args['id']
    else:
        return make_response(jsonify({
                'error' : 'Erreur lors de l\'affichage d\'un sujet: L\'identifiant n\'est pas trouvé'
                }),
                400)
    if sql_connector.is_subject_existing(sujet_id):
        try:
            return send_file(path_or_file=config.subject_folder + sujet_id + ".pdf")
        except:
            return make_response(jsonify({
                'error' : 'Erreur lors de l\'affichage d\'un sujet: Le sujet n\'est pas trouvé'
                }),
                400)
    else:
        return make_response(jsonify({
                'error' : 'Erreur lors de l\'affichage d\'un sujet: Le sujet n\'existe pas'
                }),
                400)


@app.route('/sujet/info', methods=['GET'])
def get_sujet_info():
    if 'id' in request.args:
        sujet_id = request.args['id']
    else:
        return make_response(jsonify({
                'error' : 'Erreur lors de l\'affichage d\'un sujet: L\'identifiant n\'est pas trouvé'
                }),
                400)
    if sql_connector.is_subject_existing(sujet_id):
        pass
    else:
        return make_response(jsonify({
                'error' : 'Erreur lors de l\'affichage d\'un sujet: Le sujet n\'existe pas'
                }),
                400)

    requete = 'SELECT * FROM sujet where id=%s'
    params = []
    params.append(sujet_id)
    try:
        with mysql.connector.connect(**connection_params) as db :
            with db.cursor() as c:
                c.execute(requete, params)
                result =  c.fetchone()
        username = sql_connector.get_user_info(result[8])['username']
        return jsonify({
            'id' : result[0],
            'matiere' : result[1],
            'filiere' : result[2],
            'epreuve' : result[3],
            'concours' : result[4],
            'annee' : result[5],
            'ecrit' : result[6],
            'date_ajout' : result[7],
            'username' : username
        })
    except Exception as err:
        return make_response(jsonify({
             'error' : 'mysql_connector.Error : ' + str(err)
            }),
            500)
            


## Methode pour recupérer la liste de correction d'un sujet
@app.route('/sujet/corrections', methods=['GET'])
def get_corrections_from_sujet():

    if 'id' in request.args:
        id_sujet = request.args["id"]

        if sql_connector.is_subject_existing(id_sujet):
            requete = "SELECT * from correction where id_sujet=%s"    
            params = []
            params.append(id_sujet)
            try:
                with mysql.connector.connect(**connection_params) as db :
                    with db.cursor() as c:
                        c.execute(requete, params)
                        results =  c.fetchall()
    
            except Exception as err:
                return make_response(jsonify({
                    'error' : 'mysql_connector.Error : ' + str(err)
                    }),
                    500)
            nb_results = len(results)
            pretty_result = []
            for i in range (0,nb_results):
                result_dictionnary = {}
                result_dictionnary['id'] = results[i][0]
                result_dictionnary['date_ajout'] = results[i][1]
                result_dictionnary['credit'] = results[i][2]
                result_dictionnary['username'] = sql_connector.get_user_info(results[i][3])['username']
      
                pretty_result.append(result_dictionnary)
            return make_response(
            jsonify(pretty_result),
            200)
        else:
            return make_response(jsonify({
                'error' : 'Erreur lors de a récupération des corrections: Le sujet n\'existe pas'
                }),
                400)

    else:
        return make_response(jsonify({
            'error' : 'Erreur lors de a récupération des corrections: L\identifiant du sujet n\'est pas fourni'
            }),
            400)


## Methode pour recupérer la liste de correction d'un sujet
@app.route('/sujet/commentaire', methods=['GET'])
def get_commentaire_from_sujet():

    if 'id' in request.args:
        id_sujet = request.args["id"]

        if sql_connector.is_subject_existing(id_sujet):
            requete = "SELECT * from commentaire where id_sujet=%s"    
            params = []
            params.append(id_sujet)
            try:
                with mysql.connector.connect(**connection_params) as db :
                    with db.cursor() as c:
                        c.execute(requete, params)
                        results =  c.fetchall()
    
            except Exception as err:
                return make_response(jsonify({
                    'error' : 'mysql_connector.Error : ' + str(err)
                    }),
                    500)
            try:
                nb_results = len(results)
                pretty_result = []
                for i in range (0,nb_results):
                    print(results[i])
                    result_dictionnary = {}
                    result_dictionnary['id_commentaire'] = results[i][0]
                    result_dictionnary['contenu'] = results[i][1]
                    result_dictionnary['date_ajout'] = results[i][2]
                    result_dictionnary['username'] = sql_connector.get_user_info(results[i][5])['username']
                        
                    pretty_result.append(result_dictionnary)
                return make_response(
                jsonify(pretty_result),
                200)
            except Exception as err:
                return make_response(jsonify({
                    'error' : 'Internal error : ' + str(err)
                    }),
                    500)
        else:
            return make_response(jsonify({
                'error' : 'Erreur lors de a récupération des commentaires: Le commentaire n\'existe pas'
                }),
                400)

    else:
        return make_response(jsonify({
            'error' : 'Erreur lors de a récupération des commentaire: L\identifiant du sujet n\'est pas fourni'
            }),
            400)

