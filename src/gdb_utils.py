# -*- coding: utf-8 -*-
import arcpy
import os
import tempfile


def creer_ou_obtenir_geodatabase(gdb_path):
    """
    Crée une geodatabase si elle n'existe pas et renvoie son chemin
    """
    # Extraire le chemin du répertoire et le nom de la geodatabase
    base_dir = os.path.dirname(gdb_path)
    gdb_name = os.path.basename(gdb_path)
    
    # Vérifier si le répertoire parent existe
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
        arcpy.AddMessage("Répertoire '{}' créé avec succès".format(base_dir))
    
    # Vérifier si la geodatabase existe déjà
    if not arcpy.Exists(gdb_path):
        arcpy.CreateFileGDB_management(base_dir, gdb_name)
        arcpy.AddMessage("Geodatabase '{}' créée avec succès".format(gdb_path))
    else:
        arcpy.AddMessage("Geodatabase '{}' existe déjà".format(gdb_path))
    
    return gdb_path


def sauvegarder_en_geodatabase(data, gdb_path, nom_feature_class, champ_x=None, champ_y=None):
    """
    Sauvegarde les données dans une feature class dans une geodatabase spécifiée
    """
    if data is None or data.empty:
        arcpy.AddError("Aucune donnée disponible pour créer la feature class")
        return None
    
    # Détecter automatiquement les colonnes de coordonnées
    if champ_x is None or champ_y is None:
        # Essayer d'utiliser directement les colonnes long/lat si disponibles
        if 'long' in data.columns and 'lat' in data.columns:
            champ_x = 'long'
            champ_y = 'lat'
            arcpy.AddMessage("Utilisation des colonnes existantes: X={}, Y={}".format(champ_x, champ_y))
        # Sinon essayer x/y
        elif 'x' in data.columns and 'y' in data.columns:
            champ_x = 'x'
            champ_y = 'y'
            arcpy.AddMessage("Utilisation des colonnes existantes: X={}, Y={}".format(champ_x, champ_y))
        # Sinon tenter d'extraire depuis geo_point_2d comme dans le code original
        elif 'geo_point_2d' in data.columns:
            try:
                arcpy.AddMessage("Extraction des coordonnées depuis la colonne geo_point_2d...")
                # Créer des noms temporaires pour les colonnes extraites
                temp_x = "temp_lon"
                temp_y = "temp_lat"
                
                # Extraire les coordonnées (gérer différents formats possibles)
                if isinstance(data['geo_point_2d'].iloc[0], dict):
                    data[temp_x] = data['geo_point_2d'].apply(lambda x: x.get('lon') if isinstance(x, dict) else None)
                    data[temp_y] = data['geo_point_2d'].apply(lambda x: x.get('lat') if isinstance(x, dict) else None)
                else:
                    # Si ce n'est pas un dictionnaire, tenter d'autres approches
                    arcpy.AddWarning("Format geo_point_2d inattendu, tentative d'extraction...")
                    # Vérifier si c'est une chaîne de texte à parser
                    if isinstance(data['geo_point_2d'].iloc[0], str):
                        try:
                            import json
                            data[temp_x] = data['geo_point_2d'].apply(lambda x: json.loads(x).get('lon') if x else None)
                            data[temp_y] = data['geo_point_2d'].apply(lambda x: json.loads(x).get('lat') if x else None)
                        except Exception as e:
                            arcpy.AddError("Impossible de parser la colonne geo_point_2d: {}".format(e))
                            return None
                
                # Utiliser les colonnes temporaires extraites
                champ_x = temp_x
                champ_y = temp_y
            except Exception as e:
                arcpy.AddError("Erreur lors de l'extraction des coordonnées: {}".format(e))
                return None
        else:
            arcpy.AddError("Impossible de trouver des colonnes de coordonnées utilisables")
            return None
    
    # Vérifier que les colonnes existent maintenant
    if champ_x not in data.columns or champ_y not in data.columns:
        arcpy.AddError("Les colonnes {} et/ou {} n'existent pas dans le jeu de données".format(champ_x, champ_y))
        return None
    
    # Vérifier si les coordonnées sont correctement extraites
    if data[champ_x].isnull().all() or data[champ_y].isnull().all():
        arcpy.AddError("Les coordonnées sont toutes nulles")
        return None
    
    # Debug: afficher quelques valeurs de coordonnées pour vérification
    arcpy.AddMessage("Exemple de coordonnées: X={}, Y={}".format(
        data[champ_x].iloc[0] if not data[champ_x].empty else 'N/A',
        data[champ_y].iloc[0] if not data[champ_y].empty else 'N/A'
    ))
    
    # Créer un fichier CSV temporaire
    temp_dir = tempfile.gettempdir()
    csv_path = os.path.join(temp_dir, "seine_ouest_adresses.csv")
    
    try:
        # Sauvegarder en CSV
        data.to_csv(csv_path, encoding='utf-8', index=False)
        arcpy.AddMessage("Fichier CSV temporaire créé: {}".format(csv_path))
        
        # Vérifier que le fichier CSV a été créé correctement
        if not os.path.exists(csv_path) or os.path.getsize(csv_path) == 0:
            arcpy.AddError("Le fichier CSV temporaire est vide ou n'a pas été créé")
            return None
        
        # Référence spatiale (WGS 84)
        spatial_ref = arcpy.SpatialReference(4326)
        
        # Créer une couche XY Event Layer temporaire
        temp_layer_name = "temp_layer_" + str(hash(nom_feature_class) % 10000)  # Nom unique
        arcpy.AddMessage("Création de la couche temporaire: {}".format(temp_layer_name))
        arcpy.MakeXYEventLayer_management(csv_path, champ_x, champ_y, temp_layer_name, spatial_ref)
        
        # Vérifier que la couche temporaire a été créée
        if not arcpy.Exists(temp_layer_name):
            arcpy.AddError("La couche temporaire n'a pas été créée correctement")
            return None
        
        # Chemin complet vers la feature class dans la geodatabase
        out_feature_class = os.path.join(gdb_path, nom_feature_class)
        
        # Supprimer la feature class si elle existe déjà
        if arcpy.Exists(out_feature_class):
            arcpy.Delete_management(out_feature_class)
            arcpy.AddMessage("Feature class existante '{}' supprimée".format(nom_feature_class))
        
        # Copier les entités dans une feature class permanente
        arcpy.AddMessage("Création de la feature class: {}".format(out_feature_class))
        arcpy.CopyFeatures_management(temp_layer_name, out_feature_class)
        
        # Vérifier que la feature class a été créée
        if not arcpy.Exists(out_feature_class):
            arcpy.AddError("La feature class n'a pas été créée dans la geodatabase")
            return None
        
        arcpy.AddMessage("Feature class '{}' créée avec succès dans la geodatabase avec {} entités".format(
            nom_feature_class, arcpy.GetCount_management(out_feature_class).getOutput(0)
        ))
        
        # Nettoyer
        try:
            os.remove(csv_path)
            arcpy.Delete_management(temp_layer_name)
        except:
            arcpy.AddWarning("Impossible de supprimer certains fichiers temporaires")
        
        return out_feature_class
        
    except Exception as e:
        arcpy.AddError("Erreur lors de la création de la feature class: {}".format(e))
        import traceback
        arcpy.AddError(traceback.format_exc())
        return None
    