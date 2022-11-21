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


if __name__ == "__main__":
    import test
    import user
    app.run(debug=True, port=config.port)
    




