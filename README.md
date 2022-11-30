# Preparchives-back

## Déploiement
 - Developpement mode : ```python3 app.py```
 - Installation des packets :
    - ```python3 -m pip install mysql-connector-python```
    - ```python3 -m pip install flask-jwt-extended```
    - ```python3 -m pip install Flask```
    - ```python3 -m pip install passlib```
    - ```python3 -m pip install flask_cors```


## Endpoints

 - /user/register **POST**
    - Paramètres :
        - email (obligatoire) String - Format email
        - username (obligatoire) - String
        - password (obligatoire) - String
        - nom - String 
        - prenom - String
    - Valeurs de retour :
        - Registered - Booleen
        - user (Si l'utilisateur a été créer corectement - HTTP 200)
            - date_creation - datetime
            - email - String
            - nom - String
            - prenom - String
            - username

 - /user/login **POST**
    - Paramètres :
        - username (obligatoire) - String
        - password (obligatoire) - String
    - Valeurs de retour :
        - Connected : Booleen
        - user (Si l'utilisateur a été créer corectement - HTTP 200)
            - date_creation - datetime
            - email - String
            - nom - String
            - prenom - String
            - username - String
        - Token JWT en cookies

 -  /user/logout **GET**
    - No param
    - Supprime le token jwt des cookies de l'utilisateur connecté
    - Valeurs de retour :
        - Connected : Booleen
        - user (Si l'utilisateur a été bien été déconnecté - HTTP 200)
            - date_creation - datetime
            - email - String
            - nom - String
            - prenom - String
            - username - String

 - /user **GET**
    - No param
    - Revoie les infos sur l'utilisateur connecté
    - Valeurs de retour :
        - user
            - date_creation - datetime
            - email - String
            - nom - String
            - prenom - String
            - username - String
