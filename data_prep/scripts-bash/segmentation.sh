#!/bin/bash

# Fonction pour afficher l'aide
usage() {
    echo "Usage: $0 -j <json_dir> -a <audio_dir> -o <output_dir> [-b <books>] [-h]"
    echo "  -j <json_dir>      : Répertoire contenant les fichiers JSON."
    echo "  -a <audio_dir>     : Répertoire contenant les fichiers audio."
    echo "  -o <output_dir>    : Répertoire de sortie pour les fichiers traités."
    echo "  -b <books>         : Liste des livres à traiter (séparés par des espaces, par défaut tous les livres sont traités)."
    echo "  -h                 : Afficher cette aide."
    exit 1
}

# Valeurs par défaut
json_dir=""
audio_dir=""
output_dir=""
books="GEN EXO LEV NUM DEU JOS JDG RUT 1SA 2SA 1KI 2KI 1CH 2CH EZR NEH EST JOB PSA PRO ECC SNG ISA JER LAM EZK DAN HOS JOL AMO OBA JON MIC NAM HAB ZEP HAG ZEC MAL MAT MRK LUK JHN ACT ROM 1CO 2CO GAL EPH PHP COL 1TH 2TH 1TI 2TI TIT PHM HEB JAS 1PE 2PE 1JN 2JN 3JN JUD REV"

# Traitement des arguments
while getopts "j:a:o:b:h" opt; do
    case $opt in
        j) json_dir="$OPTARG" ;;
        a) audio_dir="$OPTARG" ;;
        o) output_dir="$OPTARG" ;;
        b) books="$OPTARG" ;;   # Liste des livres, prise en charge si spécifiée
        h) usage ;;              # Afficher l'aide
        *) usage ;;
    esac
done

# Vérification des paramètres nécessaires
if [ -z "$json_dir" ] || [ -z "$audio_dir" ] || [ -z "$output_dir" ]; then
    echo "Erreur : Les paramètres json_dir, audio_dir et output_dir sont requis."
    usage
fi

# Vérification que les répertoires existent
if [ ! -d "$json_dir" ]; then
    echo "Erreur : Le répertoire JSON '$json_dir' n'existe pas."
    exit 1
fi

if [ ! -d "$audio_dir" ]; then
    echo "Erreur : Le répertoire audio '$audio_dir' n'existe pas."
    exit 1
fi

if [ ! -d "$output_dir" ]; then
    echo "Erreur : Le répertoire de sortie '$output_dir' n'existe pas."
    exit 1
fi

# Traitement des livres
for book in $books; do
    json_file="$json_dir/$book.json"
    audio_folder="$audio_dir/$book"

    # Vérification de l'existence des fichiers pour chaque livre
    if [ ! -f "$json_file" ]; then
        echo "Avertissement : Le fichier JSON pour '$book' n'existe pas. Passer au livre suivant."
        continue
    fi

    if [ ! -d "$audio_folder" ]; then
        echo "Avertissement : Le répertoire audio pour '$book' n'existe pas. Passer au livre suivant."
        continue
    fi

    # Lancer la segmentation
    echo "Traitement du livre '$book'..."
    python3 ../segmentation.py --json_path "$json_file" --audio_dir "$audio_folder" --output_dir "$output_dir/$book"
    
    if [ $? -eq 0 ]; then
        echo "Traitement réussi pour '$book'."
    else
        echo "Erreur lors du traitement de '$book'."
    fi
done

echo "Traitement terminé."

# usage
# ./segmentation.sh -j /path/to/json_files -a /path/to/audio_files -o /path/to/output_dir -b "GEN EXO PSA"
