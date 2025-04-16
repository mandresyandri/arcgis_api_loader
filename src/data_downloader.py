# -*- coding: utf-8 -*-
import ssl
import arcpy
import requests
import pandas as pd

# Désactiver la vérification SSL (à utiliser avec précaution)
ssl._create_default_https_context = ssl._create_unverified_context

# À utiliser si les données sont en API
def telecharger_donnees_api(url):
    """
    Télécharge les données d'adresses de Seine Ouest via l'API
    """
    reqUrl = url
    headersList = {
        "Accept": "*/*",
        "User-Agent": "Thunder Client (https://www.thunderclient.com)"
    }
    payload = ""
    
    try:
        response = requests.request("GET", reqUrl, data=payload, headers=headersList, verify=False)
        response.raise_for_status()  # Vérifier les erreurs HTTP
        
        # Convertir les résultats en DataFrame
        data = pd.DataFrame.from_dict(response.json()["results"])

        return data
    except Exception as e:
        arcpy.AddError("Erreur lors du téléchargement des données: {}".format(e))
        return None
    

# Principalement pour la BAN maintenant
def telecharger_donnees_url(url):
    try:
        # Téléchargement et chargement des données CSV directement dans un DataFrame
        df = pd.read_csv(url, delimiter=";", encoding="utf-8")
        
        # Retourne le DataFrame
        return df
        
    except Exception as e:
        arcpy.AddError("Erreur lors du téléchargement des données CSV: {}".format(e))
        return None
