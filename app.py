from crypt import methods
import os
from unittest import result
from flask import Flask,jsonify, request, make_response
from sqlalchemy import true
import config
import mysql.connector
import datetime
import re
import jwt          ##      https://www.bacancytechnology.com/blog/flask-jwt-authentication
from passlib.hash import sha256_crypt  ##      https://pythonprogramming.net/password-hashing-flask-tutorial/

 
connection_params = {
        'host' : config.host_db,
        'user': config.user_db,
        'password' : config.password_db,
        'database' : config.database,
        'port' : config.port_db,
    }


app = Flask(__name__)


@app.route("/")
def index():
    return "API PREPARCHIVES"

@app.route('/user/register', methods=['POST'])
def register():
    ##  Paramètres
    ##  Obligatoire : email, username, password
    ##  Optionnel : nom, prenom

    #Récupération des paramètres de la requete
    if 'email' in request.form and 'username' in request.form and 'password' in request.form:
        email = request.form["email"]
        username = request.form["username"]
        password = sha256_crypt.encrypt(request.form["password"])


    else:
        return jsonify({ 'error' : 'Register Error : No email, or username or password'})

    ## Test Pour savoir si l'email à un format valide
    pattern = "^\S+@\S+\.\S+$"
    objs = re.search(pattern, email)
    try:
        if objs.string == email:
            pass
    except:
        return jsonify({ 'error' : 'Register Error : Bad email'})

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
                    return jsonify({ 'error' : 'Register Error : Email or Username already use'})
    except Exception as err:
        return jsonify({ 'error' : 'mysql_connector. Error : ' + str(err)})


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
                return jsonify('true')

    except Exception as err:
        return jsonify({ 'error' : 'mysql_connector. Error : ' + str(err)})


@app.route('/user/login', methods=['POST'])
def login():
    ## Paramètres : 
    ## username, password

    ## Test pour savoir si les parametres sont bien passés
    if 'username' in request.form and 'password' in request.form:
        username = request.form["username"]
        password = request.form["password"]
    else:
        return jsonify({ 'error' : 'Login Error : No username or password'})

    ## Verification de l'existence d'un utilisateur
    try:
        params = []
        requete = "SELECT id,password FROM utilisateur WHERE username=%s"
        params.append(username)
        with mysql.connector.connect(**connection_params) as db :
            with db.cursor() as c:
                c.execute(requete, params)
                user =  c.fetchall()
                if not(id):
                    return jsonify({ 'error' : 'Login Error : Username not found'})
    except Exception as err:
        return jsonify({ 'error' : 'mysql_connector. Error : ' + str(err)})
    
    ## Check si un seul utilisateur existe avec cet username
    if len(user!=1):
        return jsonify({ 'error' : 'Login Error : Internal error'})

    ## Vérification du mot de passe    
    if sha256_crypt.verify(password,user[0][1]):
        return jsonify({ 'Connected' : 'true'})
    else : 
        return jsonify({ 'error' : 'Login Error : Bad Password'})


@app.route('/sujet', methods=['POST'])
def ajout_sujet():
    if 'file' in request.files:
        file = request.files['file']
        filename = 'test'
        file.save(os.path.join(config.subject_folder + filename))
    else:
        return jsonify({ 'error' : 'Subject Error : No file'})

    return 'true'



if __name__ == "__main__":
    app.run(debug=True)
    

