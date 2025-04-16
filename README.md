# Documentation d'utilisation du script

Script permettant de récupérer des données depuis une API et de le charger en geodatabase sur ArcMap ou ArcGIS Pro.

## Prérequis
- **Version de Python** : Ce script fonctionne avec Python 2.7, qui est livré avec ArcMap. Si vous utilisez ArcGIS Pro, aller à la prochaine étape
- **ArcGIS** : Assurez-vous que votre environnement est configuré pour utiliser ArcMap ou ArcGIS Pro.

> Attention, le script ne fonctionnera pas si vous n'avez pas l'un des logiciel ArcGIS avec des licences valides.

Pour télécharger le code source vous avez le choix entre git clone ou en téléchargeant le fichier. Il faudra donc le unzip. 

![image](https://github.com/user-attachments/assets/09df2a58-7a00-4110-b7ca-de9224f563f9)

> IMPORTANT ! Il faudra remplacer les éléments dans `config.ini` pour adapter à votre cas. 
```bash
gdb_path = C:\<chemin_vers_ma_geodatabase_a_creer_ou_existante>.gdb
nom_feature_class=nom_featureclass
```

## Lancer avec ArcMap
1. Localisez l'interpréteur Python fourni avec ArcMap. Par défaut, il se trouve généralement dans le répertoire suivant :
    ```
    C:/Python27/ArcGISx6410.8/python.exe
    ```
2. Identifiez le chemin complet vers le fichier `main.py` dans votre projet.

3. Exécutez la commande suivante dans votre terminal ou invite de commande, en remplaçant `<chemin_vers>` par le chemin réel vers le fichier `main.py` :
    ```
    C:/Python27/ArcGISx6410.8/python.exe c:/<chemin_vers>/main.py
    ```

## Lancer avec ArcGIS pro

1. Se placer à la racine du dossier et lancer main.py avec le bon interpréteur qui est la commande `run with ArcGIS pro`

![image](https://github.com/user-attachments/assets/ffa715bd-7e2e-4592-aeae-4ae720c3b114)

Il suffira juste de charger votre géodatabase pour accéder à la données si vous êtes sur un nouveau projet. ;) 

