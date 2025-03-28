#!/bin/bash

# Vérifie que le chemin est spécifié en argument
if [ -z "$1" ]; then
  echo "Usage: ./convert_audio.sh <mp3_directory>"
  exit 1
fi

# Définit le chemin d'accès
MP3_DIR=$1

# Exécute le script Python
python3 convert_audio.py "$MP3_DIR"
