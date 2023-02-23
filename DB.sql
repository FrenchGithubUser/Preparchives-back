CREATE DATABASE preparchive;
USE preparchive;

CREATE TABLE utilisateur (
id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
username VARCHAR(50) NOT NULL,
password VARCHAR(256) NOT NULL,
nom VARCHAR(50),
prenom VARCHAR(50),
email VARCHAR(50) NOT NULL,
date_creation TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE sujet (
id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
matiere ENUM ('Mathematiques', 'Physique-Chimie', 'Anglais', 'Français-Philo','SI','Informatique', 'Biologie') NOT NULL,
filiere ENUM ('TSI','BCPST', 'MP','PC', 'PSI','PT') NOT NULL,
epreuve ENUM ('a', 'b', 'c','d') NOT NULL,
concours VARCHAR(255) NOT NULL,
annee INT NOT NULL,
ecrit BOOLEAN NOT NULL,
date_ajout TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
id_utilisateur INT NOT NULL,
has_correction BOOLEAN,
CONSTRAINT FOREIGN KEY (id_utilisateur) REFERENCES utilisateur (id)
);


CREATE TABLE correction(
id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
date_correction TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
credit_name VARCHAR(255) NOT NULL,
credit_link VARCHAR (255),
id_utilisateur int NOT NULL,
CONSTRAINT FOREIGN KEY (id_utilisateur) REFERENCES utilisateur(id),
id_sujet int NOT NULL,
CONSTRAINT FOREIGN KEY (id_sujet) REFERENCES sujet(id)
);


CREATE TABLE commentaire (
id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
contenu VARCHAR(1000) NOT NULL,
date_commentaire TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
id_sujet int ,
CONSTRAINT FOREIGN KEY (id_sujet) REFERENCES sujet(id),
id_correction int ,
CONSTRAINT FOREIGN KEY (id_correction) REFERENCES correction(id),
id_commentaire int,
CONSTRAINT FOREIGN KEY (id_commentaire) REFERENCES commentaire(id),
id_utilisateur int NOT NULL,
CONSTRAINT FOREIGN KEY (id_utilisateur) REFERENCES utilisateur(id),
CHECK( (id_sujet IS NULL AND id_correction IS NULL AND id_commentaire IS NOT NULL) OR  (id_sujet IS NULL AND id_correction IS NOT NULL AND id_commentaire IS NULL) OR (id_sujet IS NOT NULL AND id_correction IS NULL AND id_commentaire IS NULL))
);


CREATE TABLE signalement (
id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
date_signalement TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
motif TEXT(2000) NOT NULL,
type_signalement ENUM ('insulte', 'contenue', 'autre') NOT NULL,

id_utilisateur int NOT NULL,
CONSTRAINT FOREIGN KEY (id_utilisateur) REFERENCES utilisateur(id),
id_sujet int,
CONSTRAINT FOREIGN KEY (id_sujet) REFERENCES sujet(id),
id_correction int,
CONSTRAINT FOREIGN KEY (id_correction) REFERENCES correction(id),
id_commentaire int,
CONSTRAINT FOREIGN KEY (id_commentaire) REFERENCES commentaire(id),
CHECK( (id_sujet IS NULL AND id_correction IS NULL AND id_commentaire IS NOT NULL) OR  (id_sujet IS NULL AND id_correction IS NOT NULL AND id_commentaire IS NULL) OR (id_sujet IS NOT NULL AND id_correction IS NULL AND id_commentaire IS NULL))
);

