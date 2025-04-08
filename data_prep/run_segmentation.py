from pathlib import Path
import argparse

from tqdm.auto import tqdm

from segment_audio import segment

parser = argparse.ArgumentParser()
parser.add_argument(
    "--json_path", required=True, help="Path to the JSON file. Example: data/openbible_swahili/PSA.json"
)
parser.add_argument(
    "--audio_dir",
    required=True,
    help="Path to the audio directory. Example: downloads/wavs_16/PSA/",
)
parser.add_argument("--output_dir", default="outputs/openbible_swahili/", help="Path to the output directory")
parser.add_argument("--chunk_size_s", type=int, default=15, help="Chunk size in seconds")
parser.add_argument(
        "--language",
        type=str,
        default='fr',
        required=True,
        help="Language in ISO 639-3 code. Identifying the input as Arabic, Belarusian,"
        " Bulgarian, English, Farsi, German, Ancient Greek, Modern Greek, Pontic Greek"
        ", Hebrew, Kazakh, Kyrgyz, Latvian, Lithuanian, North Macedonian, Russian, "
        "Serbian, Turkish, Ukrainian, Uyghur, Mongolian, Thai, Javanese or Yiddish "
        "will improve romanization for those languages, No effect for other languages.",
    )


def main(args):
    audio_dir = Path(args.audio_dir)
    audios = sorted(audio_dir.rglob("*.wav"))
    for audio_path in tqdm(audios, desc=f"Segmenting {audio_dir.stem}"):
        segment(audio_path, args.json_path, args.output_dir,args.language,args.chunk_size_s)


if __name__ == "__main__":
    args = parser.parse_args()
    main(args)
