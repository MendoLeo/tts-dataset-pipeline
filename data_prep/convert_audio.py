import sys
from pydub import AudioSegment
from pathlib import Path
from glob import glob
from tqdm.contrib.concurrent import process_map

def convert_mp3_to_wav(mp3_path):
    lang = mp3_path.split('/')[-2] # recuperer le nom du fichier des audios
    line = str.upper(mp3_path.split("/")[-1].replace(".mp3", ""))
    chapter= line.split('_')[4][:3] + '_' + line.split('_')[3].zfill(3)
    book = line.split('_')[4][:3]

    

    output_path_16 = f"../{lang}/wavs_16/{book}/{chapter}.wav"
    Path(output_path_16).parent.mkdir(parents=True, exist_ok=True)
    output_path_44 = f"../{lang}/wavs_44/{book}/{chapter}.wav"
    Path(output_path_44).parent.mkdir(parents=True, exist_ok=True)

    audio = AudioSegment.from_mp3(mp3_path)
    audio.export(output_path_16, format="wav", parameters=["-ar", "16000", "-ac", "1"])
    audio.export(output_path_44, format="wav", parameters=["-ar", "44100", "-ac", "1"])


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python convert_audio.py <mp3_directory>")
        sys.exit(1)

    mp3_directory = sys.argv[1]
    raw_audios = sorted(glob(f"{mp3_directory}/**/*.mp3", recursive=True))

    process_map(convert_mp3_to_wav, raw_audios)
