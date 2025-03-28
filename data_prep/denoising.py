
import os
from pathlib import Path
from tqdm import tqdm 
from .utils import denoise

def denoiser(src_path:Path, output_dir:str):
    """Appliquer la réduction du bruit aux fichiers audio."""

    # Obtenir les fichiers audio
    raw_src_audios = sorted(src_path.rglob('*.wav'))

    for src_audio in tqdm(raw_src_audios,desc='processing'):
        # Extraire les informations du chemin
        book = book = str(src_audio).split('/')[-2]
        h_audio = str(src_audio).split('/')[-1]

        # Construire le chemin de sortie
        out_audio_path = os.path.join(output_dir, book, h_audio)
        
        # Créer le répertoire de sortie si nécessaire
        os.makedirs(os.path.dirname(out_audio_path), exist_ok=True)

        # lancer le denoising
        denoise(src_audio, output_dir)

if __name__ == "__main__":
    import argparse

    # Initialisation du parser d'arguments
    parser = argparse.ArgumentParser(description="Denoise audio files in a directory")
    parser.add_argument('--src_path', type=Path, help='Chemin des fichiers audio source')
    parser.add_argument('--output_dir', type=str, help='Répertoire pour enregistrer les fichiers débruités')

    # Récupération des arguments
    args = parser.parse_args()

    # Lancer le processus de réduction du bruit
    denoiser(args.src_path, args.output_dir)
