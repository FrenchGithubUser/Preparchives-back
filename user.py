from __main__ import app

from crypt import methods
import os
from flask import Flask,jsonify, request, make_response
import config
import mysql.connector
import sql_connector
import datetime
import re
from passlib.hash import sha256_crypt  ##      https://pythonprogramming.net/password-hashing-flask-tutorial/
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

@app.route('/user/register', methods=['POST'])
def register():
    ##  Paramètres
    ##  Obligatoire : email, username, password
    ##  Optionnel : nom, prenom

    #Récupération des paramètres de la requete
    if 'email' in request.form and 'username' in request.form and 'password' in request.form:
        
        email = request.form["email"]
        if len(email)>50:
            return make_response(jsonify({
            'Registered' : False,
            'error' : 'Erreur lors de la création de compte : L\'email est trop long'
            }),
            401)

        username = request.form["username"]
        if len(username)>50:
            return make_response(jsonify({
            'Registered' : False,
            'error' : 'Erreur lors de la création de compte : Le username est trop long'
            }),
            401)

        password = sha256_crypt.encrypt(request.form["password"])       
        ## Hashage du password
        if len(password)>255:
            return make_response(jsonify({
            'Registered' : False,
            'error' : 'Erreur lors de la création de compte : Le mot de passe est trop long'
            }),
            401)


    else:
        return make_response(jsonify({
            'Registered' : False,
            'error' : 'Erreur lors de la création de compte : Email, mot de passe ou username manquant'
            }),
            401)
    ## Test Pour savoir si l'email à un format valide
    pattern = "^\S+@\S+\.\S+$"
    objs = re.search(pattern, email)
    try:
        if objs.string == email:
            pass
    except:
        return make_response(jsonify({
            'Registered' : False,
            'error' : 'Erreur lors de la création de compte : Email invalide'
            }),
            401)
    ## Test pour savoir si un email ou un username sont déja utilisés
    try:
        params = []
        requete = "SELECT * FROM utilisateur WHERE email=%s OR username=%s"
        params.append(email)
        params.append(username)
        with mysql.connector.connect(**connection_params) as db :
            with db.cursor() as c:
                c.execute(requete, params)
                results =  c.fetchall()
                if results:
                    return make_response(jsonify({
                        'Registered' : False,
                        'error' : 'Erreur lors de la création de compte : utilisateur ou email déjà utilisé'
                        }),
                        401)
    except Exception as err:
        return make_response(jsonify({
            'Registered' : False,
             'error' : 'mysql_connector.Error : ' + str(err)
            }),
            500)

    ## Cas ou le nom et le prénom ne sont pas fournis
    if not('nom' in request.form) and not('prenom' in request.form):
        requete = "INSERT into utilisateur (email, username, password) VALUES (%s,%s,%s)"
        params.append(password)

    ## Cas ou le nom est fournis
    if not('prenom' in request.form) and ('nom' in request.form):
        nom = request.form["nom"]
        requete = "INSERT into utilisateur (email, username, password, nom) VALUES (%s,%s,%s,%s)"
        params.append(password)
        params.append(nom)
    ## Cas ou le prénom est fournis
    if ('prenom' in request.form) and not('nom' in request.form):
        prenom = request.form["prenom"]
        requete = "INSERT into utilisateur (email, username, password, prenom) VALUES (%s,%s,%s,%s)"
        params.append(password)
        params.append(prenom)
    ## Cas ou le nom et le prénom sont fournis
    if ('nom' in request.form) and ('prenom' in request.form):
        nom = request.form["nom"]
        prenom = request.form["prenom"]
        requete = "INSERT into utilisateur (email, username, password, nom, prenom) VALUES (%s,%s,%s,%s,%s)"
        params.append(password)
        params.append(nom)
        params.append(prenom)

    #Envoie de la requete INSERT
    try:
        with mysql.connector.connect(**connection_params) as db :
            with db.cursor() as c:
                c.execute(requete, params)
                db.commit()
    except Exception as err:
        return make_response(jsonify({
            'Registered' : False,
             'error' : 'mysql_connector.Error : ' + str(err)
            }),
            500)
    user_id = sql_connector.get_user_id(username)
    response =  make_response(jsonify({
        'Registered' : True,
        'user' : sql_connector.get_user_info(user_id['id'])
        }),
        200)
    access_token = create_access_token(identity=user_id['id'])
    set_access_cookies(response, access_token)
    return response



@app.route('/user/login', methods=['POST'])
def login():
    ## Paramètres : 
    ## username, password

    ## Test pour savoir si les parametres sont bien passés
    if 'username' in request.form and 'password' in request.form:
        username = request.form["username"]
        password = request.form["password"]
    else:
        return make_response(jsonify({
            'Connected' : False,
            'error' : 'Erreur lors de la connection : username ou mot de passe manquant'
            }),
            401)
    ## Verification de l'existence d'un utilisateur
    try:
        params = []
        requete = "SELECT id,password FROM utilisateur WHERE username=%s or email=%s"
        params.append(username)
        params.append(username)
        with mysql.connector.connect(**connection_params) as db :
            with db.cursor() as c:
                c.execute(requete, params)
                user =  c.fetchall()
                if not(user):
                    return make_response(jsonify({
                        'Connected' : False,
                        'error' : 'Erreur lors de la connection : Username non trouvé'
                        }),
                        404)
    except Exception as err:
        return make_response(jsonify({
                        'Connected' : False,
                        'error' : 'mysql_connector. Error : ' + str(err)
                        }),
                        500)
    
    ## Check si un seul utilisateur existe avec cet username
    if len(user)!=1:
        return make_response(jsonify({
                        'Connected' : False,
                        'error' : 'Erreur lors de la connection : Internal error'
                        }),
                        500)

    ## Vérification du mot de passe    
    if not(sha256_crypt.verify(password,user[0][1])):
        return make_response(jsonify({
                        'Connected' : False,
                        'error' : 'Erreur lors de la connection : Mot de passe incorrect'
                        }),
                        401)

    ## Utilisateur connecté
    user_id = user[0][0]
    

    ## Création access token
    access_token = create_access_token(identity=user_id)
    response =  make_response(jsonify({
        'Connected' : True,
        'user' : sql_connector.get_user_info(user_id),
        'access_token' : access_token
        }),
        200)
    set_access_cookies(response, access_token)
    return make_response(response,200)


## Permet la déconnection
@app.route("/user/logout", methods=["GET"])
@jwt_required()
def logout():
    id = get_jwt_identity()
    user = sql_connector.get_user_info(id)
    response = jsonify({
        'Connected' : False,
        'msg' : 'logout successful',
        'user' : user})
    unset_jwt_cookies(response)
    return response


## Permet de récupérer les infos sur l'utilisateur connecté
@app.route("/user", methods=["GET"])
@jwt_required()
def user():
    id = get_jwt_identity()
    user = sql_connector.get_user_info(id)
    response = jsonify({
        'user' : user})
    return make_response(response,200)