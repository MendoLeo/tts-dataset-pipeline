#!/bin/bash

# Fonction pour afficher l'aide
usage() {
    echo "Usage: $0 -j <json_dir> -a <audio_dir> -o <output_dir> [-c <chunk_size>] [-b <books>] [-h]"
    echo "  -j <json_dir>      : Répertoire contenant les fichiers JSON."
    echo "  -a <audio_dir>     : Répertoire contenant les fichiers audio."
    echo "  -o <output_dir>    : Répertoire de sortie pour les fichiers traités."
    echo "  -c <chunk_size>    : Taille des segments en secondes (défaut : 15)"
    echo "  -b <books>         : Liste des livres à traiter (défaut : tous)."
    echo "  -h                 : Afficher cette aide."
    exit 1
}

# Valeurs par défaut
json_dir=""
audio_dir=""
output_dir=""
chunk_size=15
books="GEN EXO LEV NUM DEU JOS JDG RUT 1SA 2SA 1KI 2KI 1CH 2CH EZR NEH EST JOB PSA PRO ECC SNG ISA JER LAM EZK DAN HOS JOL AMO OBA JON MIC NAM HAB ZEP HAG ZEC MAL MAT MRK LUK JHN ACT ROM 1CO 2CO GAL EPH PHP COL 1TH 2TH 1TI 2TI TIT PHM HEB JAS 1PE 2PE 1JN 2JN 3JN JUD REV"

# Traitement des arguments
while getopts "j:a:o:c:b:h" opt; do
    case $opt in
        j) json_dir="$OPTARG" ;;
        a) audio_dir="$OPTARG" ;;
        o) output_dir="$OPTARG" ;;
        c) chunk_size="$OPTARG" ;;
        b) books="$OPTARG" ;;
        h) usage ;;
        *) usage ;;
    esac
done

# Vérification des paramètres nécessaires
if [ -z "$json_dir" ] || [ -z "$audio_dir" ] || [ -z "$output_dir" ]; then
    echo "Erreur : Les paramètres json_dir, audio_dir et output_dir sont requis."
    usage
fi

# Vérification des dossiers
for dir in "$json_dir" "$audio_dir"; do
    if [ ! -d "$dir" ]; then
        echo "Erreur : Le répertoire '$dir' n'existe pas."
        exit 1
    fi
done

# Création du répertoire de sortie si nécessaire
if [ ! -d "$output_dir" ]; then
    echo "Création du répertoire de sortie '$output_dir'..."
    mkdir -p "$output_dir"
fi

# Vérifie la présence du script Python
if [ ! -f ../segmentation.py ]; then
    echo "Erreur : Le fichier '../segmentation.py' est introuvable."
    exit 1
fi

# Traitement des livres
for book in $books; do
    json_file="$json_dir/$book.json"
    audio_folder="$audio_dir/$book"

    if [ ! -f "$json_file" ]; then
        echo "Avertissement : JSON manquant pour '$book'. Passage."
        continue
    fi

    if [ ! -d "$audio_folder" ]; then
        echo "Avertissement : Audio manquant pour '$book'. Passage."
        continue
    fi

    echo "Traitement du livre '$book'..."
    python3 ../segmentation.py \
        --json_path "$json_file" \
        --audio_dir "$audio_folder" \
        --output_dir "$output_dir/$book" \
        --chunk_size "$chunk_size"

    if [ $? -eq 0 ]; then
        echo "✅ Livre '$book' traité avec succès."
    else
        echo "❌ Erreur lors du traitement de '$book'."
    fi
done

echo "🎉 Traitement terminé."
