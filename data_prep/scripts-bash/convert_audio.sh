#!/bin/bash
# Script pour appeler un script Python pour convertir des fichiers audio en WAV avec un taux d'échantillonnage spécifique.
# Ce script prend en charge plusieurs extensions d'entrée avec un MP3 par défaut.

# Fonction pour afficher l'aide
usage() {
    echo "Usage: $0 -s <src_path> -o <output_dir> -t <sample_rate> [-e <extension>] [-b <books>]"
    echo "  -s <src_path>      : Chemin du répertoire source contenant les fichiers audio."
    echo "  -o <output_dir>    : Répertoire de sortie pour les fichiers WAV."
    echo "  -t <sample_rate>   : Taux d'échantillonnage en Hz (ex: 16000, 22050, 44100, 48000)."
    echo "  -e <extension>     : Extension des fichiers audio à traiter (par défaut : mp3)."
    echo "  -b <books>         : Liste des livres à traiter (optionnel, séparés par des espaces)."
    echo "  -h                 : Affiche cette aide."
    exit 1
}

# Valeurs par défaut
books="GEN EXO LEV NUM DEU JOS JDG RUT 1SA 2SA 1KI 2KI 1CH 2CH EZR NEH EST JOB PSA PRO ECC SNG ISA JER LAM EZK DAN HOS JOL AMO OBA JON MIC NAM HAB ZEP HAG ZEC MAL MAT MRK LUK JHN ACT ROM 1CO 2CO GAL EPH PHP COL 1TH 2TH 1TI 2TI TIT PHM HEB JAS 1PE 2PE 1JN 2JN 3JN JUD REV"
sample_rate="16000"  # Valeur par défaut pour le taux d'échantillonnage
extension="mp3"     # Extension par défaut

# Traitement des arguments
while getopts "s:o:t:e:b:h" opt; do
    case $opt in
        s) src_path="$OPTARG" ;;
        o) output_dir="$OPTARG" ;;
        t) sample_rate="$OPTARG" ;;  # Taux d'échantillonnage
        e) extension="$OPTARG" ;;    # Extension des fichiers audio
        b) books="$OPTARG" ;;        # Liste des livres
        h) usage ;;
        *) usage ;;
    esac
done

# Vérification des paramètres nécessaires
if [ -z "$src_path" ] || [ -z "$output_dir" ] || [ -z "$sample_rate" ]; then
    usage
fi

# Vérifier que le répertoire source existe
if [ ! -d "$src_path" ]; then
    echo "Erreur : Le répertoire source '$src_path' n'existe pas."
    exit 1
fi

# Créer le répertoire de sortie si nécessaire
mkdir -p "$output_dir"

# Traitement des fichiers audio pour chaque livre
for book in $books; do
    echo "Traitement du livre $book..."

    book_dir="$src_path/$book"
    
    # Vérifier que le répertoire du livre existe
    if [ ! -d "$book_dir" ]; then
        echo "Avertissement : Le répertoire '$book_dir' n'existe pas. Passer au livre suivant."
        continue
    fi

    # Trouver tous les fichiers audio avec l'extension spécifiée
    audio_files=$(find "$book_dir" -type f -name "*.$extension")
    
    # Vérifier qu'il y a des fichiers audio à traiter
    if [ -z "$audio_files" ]; then
        echo "Avertissement : Aucun fichier $extension trouvé dans '$book_dir'. Passer au livre suivant."
        continue
    fi

    # Appeler le script Python pour effectuer la conversion
    echo "Lancement de la conversion pour $book avec un taux d'échantillonnage de $sample_rate Hz..."
    python3 ../convert_audio.py --audio_dir "$book_dir" --sample "$sample_rate" --output_dir "$output_dir/$book" --extension "$extension"
    
    if [ $? -eq 0 ]; then
        echo "Conversion réussie pour le livre $book."
    else
        echo "Erreur lors de la conversion pour le livre $book."
    fi
done

echo "Conversion terminée pour tous les livres."

# usage example
# ./convert_audio.sh -s /chemin/vers/source -o /chemin/vers/sortie -t 22050 -e ogg
