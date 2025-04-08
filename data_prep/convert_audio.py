import sys
import argparse
from pydub import AudioSegment
from pathlib import Path
from glob import glob
from tqdm.contrib.concurrent import process_map
from functools import partial

def convert_audio(input_path, output_dir, sample_rate, extension):
    """
    Convertit un fichier audio en WAV avec le taux d'échantillonnage spécifié.
    """
    file_name = Path(input_path).stem  # Nom du fichier sans extension
    output_path = Path(output_dir) / f"{file_name}.wav"  # Suppression de la langue dans le chemin
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Charger le fichier audio en fonction de l'extension
    if extension == "mp3":
        audio = AudioSegment.from_mp3(input_path)
    elif extension == "ogg":
        audio = AudioSegment.from_ogg(input_path)
    elif extension == "flac":
        audio = AudioSegment.from_file(input_path, format="flac")
    else:
        raise ValueError(f"Extension {extension} non prise en charge")

    audio.export(output_path, format="wav", parameters=["-ar", str(sample_rate), "-ac", "1"])
    print(f"Converti : {input_path} -> {output_path} ({sample_rate} Hz)")

def main():
    parser = argparse.ArgumentParser(description="Convertir des fichiers audio en WAV avec un taux d'échantillonnage spécifique.")
    parser.add_argument("--audio_dir", type=str, required=True, help="Répertoire contenant les fichiers audio")
    parser.add_argument("--sample", type=int, choices=[16000, 22050, 44100, 48000], required=True, help="Taux d'échantillonnage en Hz (ex: 16000, 22050, 44100, 48000)")
    parser.add_argument("--output_dir", type=str, required=True, help="Répertoire de sortie pour les fichiers WAV")
    parser.add_argument("--extension", type=str, default="mp3", choices=["mp3", "ogg", "flac"], help="Extension des fichiers audio (par défaut : mp3)")

    args = parser.parse_args()
    
    # Trouver tous les fichiers audio avec l'extension spécifiée
    audio_files = sorted(glob(f"{args.audio_dir}/**/*.{args.extension}", recursive=True))

    if not audio_files:
        print(f"Aucun fichier {args.extension} trouvé dans le répertoire spécifié.")
        sys.exit(1)

    convert_audio_partial = partial(convert_audio, output_dir=args.output_dir, sample_rate=args.sample, extension=args.extension)

    process_map(convert_audio_partial, audio_files)
if __name__ == "__main__":
    main()

# usage 
# python convert_audio.py --audio_dir ./audio_files --sample 16000 --output_dir ./wav_output --extension mp3
