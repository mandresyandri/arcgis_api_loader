# -*- coding: utf-8 -*-
import arcpy
from src.data_downloader import telecharger_donnees_url
from src.gdb_utils import creer_ou_obtenir_geodatabase, sauvegarder_en_geodatabase
import ConfigParser


def main(gdb_path, nom_feature_class, url):
    # Créer ou obtenir la geodatabase
    gdb_path = creer_ou_obtenir_geodatabase(gdb_path)
    
    # Récupérer les données
    arcpy.AddMessage("Téléchargement des données de Seine Ouest...")
    data = telecharger_donnees_url(url)
    
    if data is not None:
        arcpy.AddMessage("Données téléchargées avec succès. Nombre d'enregistrements: {}".format(len(data)))
        arcpy.AddMessage("Colonnes disponibles: {}".format(", ".join(data.columns.tolist())))
        
        # Sauvegarder les données dans la geodatabase
        sauvegarder_en_geodatabase(data, gdb_path, nom_feature_class=nom_feature_class)
    
    else:
        arcpy.AddError("Impossible de créer la feature class car les données n'ont pas pu être récupérées")

if __name__ == '__main__':
    # charger les fichiers de configurations
    config = ConfigParser.ConfigParser()
    config.read("config.ini")
    gdb_path = config.get("geodata_base", "gdb_path")
    nom_feature_class = config.get("geodata_base", "nom_feature_class")
    url = config.get("lien_api", "prefix") + config.get("lien_api", "commune") + config.get("lien_api", "sufix") 

    # Lanver le script
    main(gdb_path, nom_feature_class, url)