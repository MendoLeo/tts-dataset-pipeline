import pandas as pd
import os
import json
import argparse
from glob import glob
from tqdm import tqdm

def convert_csv_to_json(directory_path):
    # Vérifier que le chemin est un répertoire valide
    if not os.path.isdir(directory_path):
        print(f"Erreur: Le chemin spécifié '{directory_path}' n'est pas un répertoire valide.")
        return

    # Créer un sous-dossier pour les fichiers JSON
    json_directory = os.path.join(directory_path, 'json_files')
    os.makedirs(json_directory, exist_ok=True)

    # Trouver tous les fichiers CSV dans le répertoire
    csv_files = glob(os.path.join(directory_path, '*.csv'))

    # Parcourir chaque fichier CSV trouvé dans le répertoire
    for csv_path in tqdm(csv_files, desc=f"Traitement des fichiers CSV dans {directory_path}"):
        # Obtenir le nom du fichier sans l'extension
        file_name = os.path.splitext(os.path.basename(csv_path))[0]
        
        # Lire le fichier CSV
        df = pd.read_csv(csv_path)
        df = df.rename(columns={df.columns[0]: 'numVerset', df.columns[1]: 'verset'})    
        
        # Convertir chaque ligne en un dictionnaire au format désiré
        data = df[['numVerset', 'verset']].to_dict(orient='records')
        
        # Sauvegarder le contenu JSON dans le sous-dossier 'json_files'
        json_path = os.path.join(json_directory, f"{file_name}.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        
        print(f"Fichier JSON créé : {json_path}")

def main():
    # Initialiser le parser d'arguments
    parser = argparse.ArgumentParser(description="Convertir des fichiers CSV en fichiers JSON")
    parser.add_argument('--directory', type=str, required=True, help="Chemin du répertoire contenant les fichiers CSV")

    # Récupérer les arguments
    args = parser.parse_args()

    # Appeler la fonction pour effectuer la conversion
    convert_csv_to_json(args.directory)

if __name__ == "__main__":
    main()


# usage
# python csv_to_json.py --directory "/chemin/vers/le/dossier"
