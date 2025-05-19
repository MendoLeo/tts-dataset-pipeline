#!/bin/bash

# Fonction pour afficher l'aide
usage() {
    echo "Usage: $0 -a <audio_dir> -o <output_dir> [-b <books>] [-t <threshold>] [-h]"
    echo "  -a <audio_dir>     : Répertoire contenant les fichiers audio segmentés."
    echo "  -o <output_dir>    : Répertoire de sortie pour les segments filtrés."
    echo "  -t <threshold>     : Seuil pour retirer les mauvaises alignements (par défaut : -0.2)"
    echo "  -b <books>         : Liste des livres à traiter (par défaut : tous les livres)."
    echo "  -h                 : Afficher cette aide."
    exit 1
}

# Valeurs par défaut (PAS d'espaces autour du `=`)
audio_dir=""
output_dir=""
threshold=-0.2
books="GEN EXO LEV NUM DEU JOS JDG RUT 1SA 2SA 1KI 2KI 1CH 2CH EZR NEH EST JOB PSA PRO ECC SNG ISA JER LAM EZK DAN HOS JOL AMO OBA JON MIC NAM HAB ZEP HAG ZEC MAL MAT MRK LUK JHN ACT ROM 1CO 2CO GAL EPH PHP COL 1TH 2TH 1TI 2TI TIT PHM HEB JAS 1PE 2PE 1JN 2JN 3JN JUD REV"

# Traitement des options
while getopts "a:o:t:b:h" opt; do
    case $opt in
        a) audio_dir="$OPTARG" ;;
        o) output_dir="$OPTARG" ;;
        t) threshold="$OPTARG" ;;
        b) books="$OPTARG" ;;
        h) usage ;;
        *) usage ;;
    esac
done

# Vérification des paramètres nécessaires
if [ -z "$audio_dir" ] || [ -z "$output_dir" ]; then
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

    if [ ! -d "$audio_folder" ]; then
        echo "Avertissement : Le répertoire audio pour '$book' n'existe pas. Passage au livre suivant."
        continue
    fi

    echo "Filtrage du livre '$book'..."
    python3 ../run_filter.py --audio_dir "$audio_folder" --output_dir "$output_dir/$book" --probability_difference_threshold "$threshold"

    if [ $? -eq 0 ]; then
        echo "Filtrage réussi pour '$book'."
    else
        echo "Erreur lors du filtrage de '$book'."
    fi
done

echo "Traitement terminé."
