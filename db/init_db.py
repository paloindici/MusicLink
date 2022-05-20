import os
import sqlite3
from os.path import exists


def gestion_fichier_database():
    """
    Vérifie la présence d'un fichier de base de données (+ tentative de création si non trouvée) et retourne le chemin

    :return: Chemin exact ou le fichier de données est disponible
    """
    location_docker = "/data/database.db"
    location_windows = location_docker[6:]

    if not exists(location_docker) and not exists(location_windows):
        print(f"Base de données - Tentative de création sur le volume Docker...")
        try:
            connection = sqlite3.connect(location_docker)
            with open('./db/schema.sql') as f:
                connection.executescript(f.read())
            connection.commit()
            connection.close()
        except:
            print(f"Base de données - Erreur pendant la création du fichier {location_docker} sur le volume docker.")
        if os.path.isfile(location_docker):
            print(f"Base de données - Fichier {location_docker} existe maintenant sur le volume docker.")
            return location_docker

        print(f"Base de données - Tentative de création sur Windows...")
        try:

            connection = sqlite3.connect(location_windows)
            with open('./db/schema.sql') as f:
                connection.executescript(f.read())
            connection.commit()
            connection.close()
        except:
            print(f"Base de données - Erreur pendant la création du fichier {location_windows} sur windows.")
        if os.path.isfile(location_windows):
            print(f"Base de données - Fichier {location_windows} existe maintenant sur Windows.")
            return location_windows
        else:
            print(f"Base de données - Fichier {location_windows} n'existe toujours pas sur Windows.")
            print(f"Impossible de créer ou d'accéder a un fichier de base de données")
            return None
    elif exists(location_docker):
        return location_docker
    else:
        return location_windows
