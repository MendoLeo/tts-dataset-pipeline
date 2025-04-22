from pathlib import Path
import argparse
import shutil
import csv
from tqdm.auto import tqdm
from datetime import datetime

from filter_audio import compute_probability_difference, compute_probability_difference_batched

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--audio_dir", required=True, help="Directory with audio and text files.")
    parser.add_argument("--output_dir", default="outputs/data_filtered/", help="Output directory for filtered files.")
    parser.add_argument("--language", required=True, type=str, help="Language ISO 639-3 code.")
    parser.add_argument("--chunk_size_s", type=int, default=15, help="Chunk size in seconds.")
    parser.add_argument("--probability_difference_threshold", type=float, default=-0.2, help="Threshold for filtering.")
    parser.add_argument("--batched", action="store_true", help="Enable batch processing.")
    parser.add_argument("--batch_size", type=int, default=16, help="Batch size if batched mode is used.")
    return parser.parse_args()

def setup_logging(output_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=True)
    log_f = output_dir / "log.txt"
    return log_f

def process_file(audio_path, transcript_path, prob_diff, threshold, output_dir, log_f):
    if prob_diff > threshold:
        shutil.copy(audio_path, output_dir / audio_path.name)
        shutil.copy(transcript_path, output_dir / transcript_path.name)
        return True
    else:
        with open(log_f, "a") as f:
            f.write(f"[{datetime.now()}] Rejected: {audio_path.name} (diff: {prob_diff:.3f})\n")
        return False

def main(args):
    audio_dir = Path(args.audio_dir)
    output_dir = Path(args.output_dir)
    log_f = setup_logging(output_dir)

    audio_files = sorted(audio_dir.glob("*.wav"))
    transcript_files = {f.stem: f for f in audio_dir.glob("*.txt")}

    retained = 0
    rejected = 0

    if not args.batched:
        for audio_path in tqdm(audio_files, desc="Filtering"):
            stem = audio_path.stem
            if stem not in transcript_files:
                print(f"Missing transcript for {audio_path.name}")
                continue

            with open(transcript_files[stem]) as f:
                transcript = f.read()

            prob_diff = compute_probability_difference(audio_path, transcript, args.language, args.chunk_size_s)

            if process_file(audio_path, transcript_files[stem], prob_diff, args.probability_difference_threshold, output_dir, log_f):
                retained += 1
            else:
                rejected += 1
    else:
        valid_pairs = [(a, transcript_files[a.stem]) for a in audio_files if a.stem in transcript_files]
        transcripts = [open(t).read() for _, t in valid_pairs]
        audio_paths = [a for a, _ in valid_pairs]

        prob_diffs = compute_probability_difference_batched(audio_paths, transcripts, args.language, args.batch_size)

        for audio_path, transcript_path, prob_diff in zip(audio_paths, [t for _, t in valid_pairs], prob_diffs):
            if process_file(audio_path, transcript_path, prob_diff, args.probability_difference_threshold, output_dir, log_f):
                retained += 1
            else:
                rejected += 1

    print(f"\n✅ Done. Retained: {retained} | Rejected: {rejected}")

if __name__ == "__main__":
    args = parse_args()
    main(args)
