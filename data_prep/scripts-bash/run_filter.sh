#!/bin/bash

# Fonction pour afficher l'aide
usage() {
    echo "Usage: $0 -a <audio_dir> -o <output_dir> [-b <books>] [-h]"
    echo "  -a <audio_dir>     : Répertoire contenant les fichiers audio segmentés."
    echo "  -o <output_dir>    : Répertoire de sortie pour les segments filtrés."
    echo "  -t <th>            : threshold for bad alignemet removing"
    echo "  -b <books>         : Liste des livres à traiter (séparés par des espaces, par défaut tous les livres sont traités)."
    echo "  -h                 : Afficher cette aide."
    exit 1
}

# Valeurs par défaut
audio_dir=""
output_dir=""
th        = -0.2
books="GEN EXO LEV NUM DEU JOS JDG RUT 1SA 2SA 1KI 2KI 1CH 2CH EZR NEH EST JOB PSA PRO ECC SNG ISA JER LAM EZK DAN HOS JOL AMO OBA JON MIC NAM HAB ZEP HAG ZEC MAL MAT MRK LUK JHN ACT ROM 1CO 2CO GAL EPH PHP COL 1TH 2TH 1TI 2TI TIT PHM HEB JAS 1PE 2PE 1JN 2JN 3JN JUD REV"

# Traitement des arguments
while getopts "a:o:t:b:h" opt; do
    case $opt in
        a) audio_dir="$OPTARG" ;;
        o) output_dir="$OPTARG" ;;
        t) th="$OPTARG" ;; # threshold of filtering
        b) books="$OPTARG" ;;   # Liste des livres, prise en charge si spécifiée
        h) usage ;;              # Afficher l'aide
        *) usage ;;
    esac
done

# Vérification des paramètres nécessaires
if [ -z "$audio_dir" ] || [ -z "$output_dir" ] || [ -z "$th" ] ; then
    echo "Erreur : Les paramètres audio_dir et output_dir sont requis."
    usage
fi

# Vérification que les répertoires existent
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
    audio_folder="$audio_dir/$book"
    
    # Vérification de l'existence du répertoire audio pour chaque livre
    if [ ! -d "$audio_folder" ]; then
        echo "Avertissement : Le répertoire audio pour '$book' n'existe pas. Passer au livre suivant."
        continue
    fi
    
    # Lancer le filtrage
    echo "Filtrage du livre '$book'..."
    python3 ../run_filter.py --audio_dir "$audio_folder" --output_dir "$output_dir/$book"  --probability_difference_threshold "$th" 
    
    if [ $? -eq 0 ]; then
        echo "Filtrage réussi pour '$book'."
    else
        echo "Erreur lors du filtrage de '$book'."
    fi
done

echo "Traitement terminé."

# usage
# ./run_filter.sh -a /path/to/audio_files -o /path/to/output_dir -b "GEN EXO PSA"
