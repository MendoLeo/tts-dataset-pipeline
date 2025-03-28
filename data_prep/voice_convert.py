import os
import argparse
from tqdm import tqdm
from  pathlib import Path
from  TTS import TTS # no yet handle by the framework

def process_audio(src_path:Path, target_audio):

    """" Cette fonction a pour but de cloner la voix d'un repertoire d'audios en 
    une nouvelle voix cible en utilisant un modèle TTS et une librairie TTS.

    Args:
        src_path (Path): Le chemin du répertoire d'audios source
        target_audio (str): Le chemin de l'audio cible(voix a cloner)
    """
    # Initialiser le modèle TTS

    tts = TTS(model_name="voice_conversion_models/multilingual/vctk/freevc24", progress_bar=True).to("cuda")
        
# Obtenir la liste des fichiers source audio
    raw_src_audios = sorted(src_path.rglob("*.wav"))  

    for src_audio in tqdm(raw_src_audios,desc='processing'):
        # Extraire le livre et le fichier audio
        book = str(src_audio).split('/')[-2]
        h_audio = str(src_audio).split('/')[-1]

        # Construire le chemin de sortie
        out_audios = f"/wavs_16/{book}/{h_audio}"
        
        # Créer les répertoires de sortie si nécessaire
        os.makedirs(os.path.dirname(out_audios), exist_ok=True)
        # Convertir le fichier audio
        tts.voice_conversion_to_file(source_wav=src_audio, target_wav=target_audio, file_path=out_audios)

if __name__ == "__main__":
    # Initialisation du parser d'arguments
    parser = argparse.ArgumentParser(description="Audio processing script")
    parser.add_argument('src_path', type=Path, help='Le chemin des fichiers audio source')
    parser.add_argument('target_audio', type=str, help='Le chemin de l\'audio cible')

    # Récupération des arguments
    args = parser.parse_args()

    # Lancer le processus avec les chemins fournis
    process_audio(args.src_path, args.target_audio)
