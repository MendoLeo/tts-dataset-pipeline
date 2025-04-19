#!/bin/bash

# Script shell de lancement du traitement par align_batch.py
# Usage :
# ./align_batch_launcher.sh \
#   --audio_dir "/chemin/vers/audios" \
#   --text_dir "/chemin/vers/textes" \
#   --output_dir "/chemin/vers/output" \
#   [--language fr] [--romanize] [--segment_audio] [--generate_txt] ...

# Lancer le script Python avec tous les arguments passés
python align_batch.py "$@"
