# Preparchives-back

## Déploiement
 - Developpement mode : ```python3 app.py```
 - Installation des packets :
    - ```python3 -m pip install mysql-connector-python```
    - ```python3 -m pip install flask-jwt-extended```
    - ```python3 -m pip install Flask```
    - ```python3 -m pip install passlib```
    - ```python3 -m pip install flask_cors```
    - ```python3 -m pip install validators```



## Endpoints

- /commentaire (méthode POST) 
  - Permet de poster un commentaire. Il y a des vérifications pour s'assurer que le contenu du commentaire est présent et a une longueur adéquate, ainsi que pour vérifier que les id_sujet ou id_commentaire fournis sont valides et existants dans la base de données. Il faut inclure dans le body de la requête les paramètres suivants : 'contenu' (string), 'id_sujet' (integer) ou 'id_commentaire' (integer). La fonction signature de la méthode est ajout_commentaire()

- /signalement (méthode POST) 
  - Permet de signaler un sujet, une correction ou un commentaire. Il y a des vérifications pour s'assurer que les informations nécessaires (motif, type_signalement, id_sujet, id_correction ou id_commentaire) sont présentes et valides. Il faut inclure dans le body de la requête les paramètres suivants : 'motif' (string), 'type_signalement' (string) et 'id_sujet' (integer), 'id_correction' (integer) ou 'id_commentaire' (integer). Signature : `ajout_signalement

- /user/login (méthode POST) 
  - Permet à un utilisateur de se connecter en fournissant son nom d'utilisateur et son mot de passe. Il faut inclure dans le body de la requête les paramètres suivants : 'username' (string) et 'password' (string). Si les informations sont correctes, un jeton d'accès est créé et renvoyé. Signature : login():

- /user/logout (méthode GET) 
Permet à un utilisateur de se déconnecter en supprimant le jeton d'accès en cours. Il n'y a pas de paramètres à inclure dans la requête. Signature : logout():

- /user (méthode GET)
  -  Permet de récupérer les informations d'un utilisateur en fournissant son nom d'utilisateur ou son adresse email. Il faut inclure dans la requête l'un des paramètres suivants Permet'username' (string) ou 'email' (string). Signature \Nget_user():

- /sujet/search (méthode GET)
  -   Permet de poster un sujet. Il y a des vérifications pour s'assurer que le fichier, la matière, l'épreuve, la filière et le concours sont présents et conformes, ainsi que pour vérifier que les id_sujet fournis sont valides et existants dans la base de données. Il faut inclure dans le body de la requête les paramètres suivants : 'file' (pdf), 'matiere' (string), 'epreuve' (string), 'filiere' (string) et 'concours' (string). Signature : ajout_sujet()

- /sujet (méthode POST)
  -  Permet de rechercher des sujets en fonction de différents paramètres tels que la matière, la filière, l'épreuve, l'année et le type de concours. Il y a des vérifications pour s'assurer que les paramètres fournis sont conformes et existants dans la base de données. Il faut inclure dans les paramètres de la requête les paramètres suivants : 'matiere' (string), 'filiere' (string), 'epreuve' (string), 'annee' (integer) et 'ecrit' (integer). Signature : search_sujet()

- /sujet/pdf (méthode GET)
  -  Permet de récupérer le fichier pdf d'un sujet en fonction de son identifiant. Il y a une vérification pour s'assurer que l'identifiant fourni est valide et existant dans la base de données. Il faut inclure dans les paramètres de la requête le paramètre 'id' (integer). Signature : get_sujet_pdf().

- /sujet/info (méthode GET)
  -  Permet de récupérer les informations d'un sujet en fonction de son identifiant. Il y a une vérification pour s'assurer que l'identifiant fourni est valide et existant dans la base de données. Il faut inclure dans les paramètres de la requête le paramètre 'id' (integer). Signature : get_sujet_info(). Les informations retournées incluent l'identifiant, la matière, la filière, l'épreuve, le concours, l'année, le type de concours, la date d'ajout, le nom d'utilisateur de l'utilisateur qui a ajouté le sujet et si le sujet a une correction ou non.

- /sujet/corrections (méthode GET)
  -  Permet de récupérer la liste de corrections d'un sujet en fonction de son identifiant. Il y a une vérification pour s'assurer que l'identifiant fourni est valide et existant dans la base de données. Il faut inclure dans les paramètres de la requête le paramètre 'id' (integer). Les informations retournées incluent l'id, la date d'ajout, le crédit, le nom d'utilisateur de l'utilisateur qui a ajouté la correction et si la correction a un crédit ou non. Signature : get_corrections_from_sujet().

- /sujet/commentaire (méthode GET)
  -  Permet de poster un commentaire. L'endpoint vérifie que le contenu du commentaire est présent et qu'il a une longueur adéquate, ainsi que pour vérifier que les id_sujet ou id_commentaire fournis sont valides et existants dans la base de données. Il faut inclure dans le corps de la requête les paramètres suivants : 'contenu' (string), 'id_sujet' (integer) ou 'id_commentaire' (integer). La fonction signature de la méthode est ajout_commentaire().

- /correction (méthode POST)
  -  Permet de publier une correction. Il y a des vérifications pour s'assurer que le fichier de correction est présent et a une extension adéquate, que le nom de crédit est présent et a une longueur adéquate, ainsi que pour vérifier que l'id_sujet fourni est valide et existant dans la base de données. Il faut inclure dans le body de la requête les paramètres suivants : 'file' (fichier), 'credit_name' (string), 'credit_link' (string) et 'id_sujet' (integer). Signature : ajout_correction()

- /correction/info (méthode GET)
  -  Permet de récupérer les informations d'une correction telle que le nom du crédit, le nom d'utilisateur et la date de correction. Il y a une vérification pour s'assurer que l'id de correction fourni est valide et existant dans la base de données. Il faut inclure dans les paramètres de la requête l'id de la correction sous la forme 'id' (integer). Signature : get_correction_info()
