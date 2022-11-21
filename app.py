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

 



app = Flask(__name__)


@app.route("/")
def index():
    return "API PREPARCHIVES"


@app.route('/sujet', methods=['POST'])
def ajout_sujet():
    if 'file' in request.files:
        file = request.files['file']
        filename = 'test'
        file.save(os.path.join(config.subject_folder + filename))
    else:
        return jsonify({ 'error' : 'Erreur lors de l\'envoi d\'un sujet : pas de fichier'})

    return 'true'





if __name__ == "__main__":
    import test
    import user
    app.run(debug=True)


