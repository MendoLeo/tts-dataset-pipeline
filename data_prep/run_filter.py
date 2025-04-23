from pathlib import Path
import argparse
import shutil
import csv
from tqdm.auto import tqdm
from datetime import datetime

from filter_audio import compute_probability_difference, compute_probability_difference_batched
from alignment_utils import write_book_stats

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--audio_dir",
        required=True,
        help="Path to the audio directory, must contain txt files with the same name. Example: outputs/data/PSA/",
    )
    parser.add_argument("--output_dir", default="outputs/data_filtered/", help="Path to the output directory")
    parser.add_argument("--language", required=True, type=str, help="Language in ISO 639-3 code.")
    parser.add_argument("--chunk_size_s", type=int, default=15, help="Chunk size in seconds")
    parser.add_argument(
        "--probability_difference_threshold",
        type=float,
        default=-0.2,
        help="Probability difference threshold for filtering. Default: -0.2 from MMS.",
    )
    parser.add_argument(
        "--batched",
        action="store_true",
        help="Whether to batch-filter. Currently still just on-par with non-batched filtering.",
    )
    parser.add_argument(
        "--batch_size",
        type=int,
        default=16,
        help="Batch size for batch-filtering. Default to 16 (usable for P100 16GB).",
    )
    return parser.parse_args()

def setup_logging(output_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=True)
    log_f = output_dir / "log_file.txt"
    history_f = output_dir / "history.csv"

    if not log_f.exists():
        with open(log_f, "w") as f:
            f.write("Rejected Files Log\n===================\n")
    
    if not history_f.exists():
        with open(history_f, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Book", "Retained", "Rejected"])

    return log_f, history_f

def process_file(audio_path, transcript_path, probability_difference, threshold, output_dir, base_dir_name, log_f):
    chapter = audio_path.parent.stem

    output_path = output_dir / base_dir_name / chapter
    output_path.mkdir(parents=True, exist_ok=True)

    if probability_difference > threshold:
        shutil.copy(audio_path, output_path / audio_path.name)
        shutil.copy(transcript_path, output_path / transcript_path.name)
        return True
    else:
        with open(log_f, "a") as log_file:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_file.write(f"[{timestamp}] Rejected: {audio_path} (Difference: {probability_difference})\n")
        return False

def main(args):
    audio_dir = Path(args.audio_dir)
    output_dir = Path(args.output_dir)
    log_f, history_f = setup_logging(output_dir)

    audios = sorted(audio_dir.rglob("**/*.wav"))
    base_dir_name = audio_dir.stem

    current_book = None
    retained_count = 0
    rejected_count = 0

    if not args.batched:
        for audio_path in tqdm(audios, desc=f"Filtering {base_dir_name}"):
            transcript_path = audio_path.with_suffix(".txt")
            if not transcript_path.exists():
                print(f"Transcript not found for: {audio_path}")
                continue

            book_name = audio_path.parent.parent.stem
            if current_book != book_name:
                if current_book is not None:
                    write_book_stats(current_book, retained_count, rejected_count, history_f)
                current_book = book_name
                retained_count = 0
                rejected_count = 0

            with open(transcript_path) as f:
                ground_truth = f.read()

            prob_diff = compute_probability_difference(audio_path, ground_truth, args.language, args.chunk_size_s)

            if process_file(audio_path, transcript_path, prob_diff, args.probability_difference_threshold, output_dir, base_dir_name, log_f):
                retained_count += 1
            else:
                rejected_count += 1

        if current_book is not None:
            write_book_stats(current_book, retained_count, rejected_count, history_f)

    else:
        transcript_paths = [a.with_suffix(".txt") for a in audios]
        ground_truths = []
        valid_pairs = []

        for audio, transcript in zip(audios, transcript_paths):
            if transcript.exists():
                with open(transcript) as f:
                    ground_truths.append(f.read())
                valid_pairs.append((audio, transcript))
            else:
                print(f"Transcript not found for: {audio}")

        valid_audios = [pair[0] for pair in valid_pairs]
        valid_transcripts = [pair[1] for pair in valid_pairs]

        prob_diffs = compute_probability_difference_batched(valid_audios, ground_truths, args.language, args.batch_size)

        for audio_path, transcript_path, prob_diff in zip(valid_audios, valid_transcripts, prob_diffs):
            book_name = audio_path.parent.parent.stem
            if current_book != book_name:
                if current_book is not None:
                    write_book_stats(current_book, retained_count, rejected_count, history_f)
                current_book = book_name
                retained_count = 0
                rejected_count = 0

            if process_file(audio_path, transcript_path, prob_diff, args.probability_difference_threshold, output_dir, base_dir_name, log_f):
                retained_count += 1
            else:
                rejected_count += 1

        if current_book is not None:
            write_book_stats(current_book, retained_count, rejected_count, history_f)

if __name__ == "__main__":
    args = parse_args()
    main(args)
