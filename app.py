from crypt import methods
from unittest import result
from flask import Flask,jsonify, request
import config
import mysql.connector
import datetime

 
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

@app.route('/user/register', methods=['GET'])
def register():

    #Récupération des paramètres de la requete
    if 'email' in request.args and 'username' in request.args and 'password' in request.args:
        email = request.args.get("email")
        username = request.args.get("username")
        nom = request.args.get("nom")
        prenom = request.args.get("prenom")
        password = request.args.get("password")
    else:
        return jsonify({ 'error' : 'Register Error : No email, or username or password'})

    ## Test pour savoir si un email ou un username est déja utilisé
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
    if not('nom' in request.args) and not('nom' in request.args):
        requete = "INSERT into utilisateur (email, username, password) VALUES (%s,%s,%s)"
        params.append(password)

    ## Cas ou le nom est fournis
    if not('nom' in request.args) and ('nom' in request.args):
        requete = "INSERT into utilisateur (email, username, password, nom) VALUES (%s,%s,%s,%s)"
        params.append(password)
        params.append(nom)
    ## Cas ou le prénom est fournis
    if ('nom' in request.args) and not('nom' in request.args):
        requete = "INSERT into utilisateur (email, username, password, prenom) VALUES (%s,%s,%s,%s)"
        params.append(password)
        params.append(prenom)
    ## Cas ou le nom et le prénom sont fournis
    if ('nom' in request.args) and ('nom' in request.args):
        requete = "INSERT into utilisateur (email, username, password, nom, prenom) VALUES (%s,%s,%s,%s,%s)"
        params.append(password)
        params.append(nom)
        params.append(prenom)

    try:
        with mysql.connector.connect(**connection_params) as db :
            with db.cursor() as c:
                c.execute(requete, params)
                db.commit()
                return jsonify('true')

    except Exception as err:
        return jsonify({ 'error' : 'mysql_connector. Error : ' + str(err)})




    
@app.route('/bdd/wallet', methods=['GET'])
def get():
    try:
        with mysql.connector.connect(**connection_params) as db :
            with db.cursor() as c:
                c.execute(requete, params)
                results =  c.fetchall()
                if results :
                    return jsonify(results) 
                else :
                    return jsonify()

    except Exception as err:
        return jsonify({ 'error' : 'mysql_connector. Error : ' + str(err)})
        

if __name__ == "__main__":
    app.run(debug=True)


