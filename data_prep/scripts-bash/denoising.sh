#!/bin/bash
# Execute this if you name yours book and want to handle them all with juste one line of code

# Fonction pour afficher l'aide
usage() {
    echo "Usage: $0 -s <src_path> -o <output_dir> [-b <books>]"
    echo "  -s <src_path>      : Chemin du répertoire source contenant les fichiers audio."
    echo "  -o <output_dir>    : Répertoire de sortie pour les fichiers débruités."
    echo "  -b <books>         : Liste des livres séparés par des espaces (optionnel)."
    exit 1
}

# Valeurs par défaut
books="GEN EXO LEV NUM DEU JOS JDG RUT 1SA 2SA 1KI 2KI 1CH 2CH EZR NEH EST JOB PSA PRO ECC SNG ISA JER LAM EZK DAN HOS JOL AMO OBA JON MIC NAM HAB ZEP HAG ZEC MAL MAT MRK LUK JHN ACT ROM 1CO 2CO GAL EPH PHP COL 1TH 2TH 1TI 2TI TIT PHM HEB JAS 1PE 2PE 1JN 2JN 3JN JUD REV"

# Traitement des arguments
while getopts "s:o:b:h" opt; do
    case $opt in
        s) src_path="$OPTARG" ;;
        o) output_dir="$OPTARG" ;;
        b) books="$OPTARG" ;; # Si une liste de livres est fournie
        h) usage ;;
        *) usage ;;
    esac
done

# Vérification des paramètres nécessaires
if [ -z "$src_path" ] || [ -z "$output_dir" ]; then
    usage
fi

# Boucle pour traiter chaque livre
for book in $books; do 
    echo "Traitement de $book..." 
    python3 ../denoising.py --src_path "$src_path/$book" --output_dir "$output_dir" --extension wav
done

# usage: inter in scripts-bash en execute ./denoising.sh options