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
    return "API EDMEE"

@app.route('/bdd/', methods=['GET'])
def get_user():
    pass
    
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


