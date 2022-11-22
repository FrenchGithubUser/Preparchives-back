# Preparchives-back

## Déploiement
 - Developpement mode : ```python3 app.py```


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
            - username
