from pathlib import Path
import argparse
import shutil
import csv
from tqdm.auto import tqdm
from datetime import datetime

from filter_audio import compute_probability_difference, compute_probability_difference_batched
from utils import write_book_stats

parser = argparse.ArgumentParser()
parser.add_argument(
    "--audio_dir",
    required=True,
    help="Path to the audio directory, must contain txt files with the same name. Example: outputs/openbible_swahili/PSA/",
)
parser.add_argument("--output_dir", default="outputs/openbible_swahili_filtered/", help="Path to the output directory")
parser.add_argument("--chunk_size_s", type=int, default=15, help="Chunk size in seconds")
parser.add_argument(
    "--probability_difference_threshold",
    type=float,
    default=-0.3,
    help="Probability difference threshold for filtering. Default: -0.2 from MMS.",
)
parser.add_argument(
    "--batched",
    action="store_true",
    help="Whether to batch-filter. Currently still just on-par with non-batched filtering.",)
parser.add_argument(
    "--batch_size",
    type=int,
    default=16,
    help="Batch size for batch-filtering. Default to 16 (usable for P100 16GB).",
)
parser.add_argument(
    "--log_file",
    default="rejected_files_log.txt",
    help="Path to the log file for storing rejected file names. Default: rejected_files_log.txt in the current directory.",
)
parser.add_argument(
    "--history_file",
    default="history.csv",
    help="Path to the CSV file for storing book-level statistics. Default: history.csv in the current directory.",
)

def main(args):
    audio_dir = Path(args.audio_dir)
    audios = sorted(audio_dir.rglob("*/*.wav"))

    # Prepare log file
    log_file_path = Path(args.log_file)
    log_file_path.parent.mkdir(parents=True, exist_ok=True)

    # Check if log file exists
    log_file_exists = log_file_path.exists()
    with open(log_file_path, "a") as log_file:
        if not log_file_exists:
            log_file.write("Rejected Files Log\n")
            log_file.write("===================\n")

    # Prepare history file
    history_file_path = Path(args.history_file)
    history_file_path.parent.mkdir(parents=True, exist_ok=True)

    # Check if history file exists
    history_file_exists = history_file_path.exists()
    if not history_file_exists:
        with open(history_file_path, "w", newline="") as history_file:
            csv_writer = csv.writer(history_file)
            csv_writer.writerow(["Book", "Retained", "Rejected"])  # Header

    # Process each book
    current_book = None
    retained_count = 0
    rejected_count = 0

    """def write_book_stats(book_name):
        # Helper function to write stats to the CSV
        nonlocal retained_count, rejected_count
        if book_name:
            with open(history_file_path, "a", newline="") as history_file:
                csv_writer = csv.writer(history_file)
                csv_writer.writerow([book_name, retained_count, rejected_count])
            retained_count = 0
            rejected_count = 0"""
            

    if not args.batched:
        for audio_path in tqdm(audios, desc=f"Filtering {audio_dir.stem}"):
            transcript_path = audio_path.with_suffix(".txt")
            book_name = audio_path.parent.parent.stem  # Assuming directory structure: /{book}/{chapter}/{file}

            # Detect book change and write stats
            if current_book != book_name:
                write_book_stats(current_book, retained_count, rejected_count, history_file_path)
                #write_book_stats(current_book)
                current_book = book_name

            # Create output directory `output_dir/{book}/{chapter}/`
            output_path = Path(args.output_dir) / audio_dir.stem / audio_path.parent.stem
            output_audio_path = output_path / audio_path.name
            output_transcript_path = output_path / transcript_path.name
            output_audio_path.parent.mkdir(parents=True, exist_ok=True)

            # Read ground truth
            with open(transcript_path) as f:
                ground_truth = f.read()

            # Compute probability difference
            probability_difference = compute_probability_difference(audio_path, ground_truth, args.chunk_size_s)

            # Copy audio and transcript if probability_difference is greater than threshold
            if probability_difference > args.probability_difference_threshold:
                shutil.copy(audio_path, output_audio_path)
                shutil.copy(transcript_path, output_transcript_path)
                retained_count += 1
            else:
                # Log the rejected audio path and probability difference
                with open(log_file_path, 'a') as log_file:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    log_file.write(f"[{timestamp}] Rejected: {audio_path} (Difference: {probability_difference})\n")
                rejected_count += 1

        # Write stats for the last book
        write_book_stats(current_book, retained_count, rejected_count, history_file_path)
        
        #write_book_stats(current_book)

    else:
        # Read ground truth
        transcript_paths = [audio.with_suffix(".txt") for audio in audios]
        ground_truths = []
        for transcript_path in transcript_paths:
            with open(transcript_path) as f:
                ground_truths.append(f.read())

        probability_differences = compute_probability_difference_batched(audios, ground_truths, args.batch_size)
        for audio_path, probability_difference in zip(audios, probability_differences):
            transcript_path = audio_path.with_suffix(".txt")
            book_name = audio_path.parent.parent.stem  # Assuming directory structure: /{book}/{chapter}/{file}

            # Detect book change and write stats
            if current_book != book_name:
                write_book_stats(current_book)
                current_book = book_name

            # Create output directory `output_dir/{book}/{chapter}/`
            output_path = Path(args.output_dir) / audio_dir.stem / audio_path.parent.stem
            output_audio_path = output_path / audio_path.name
            output_transcript_path = output_path / transcript_path.name
            output_audio_path.parent.mkdir(parents=True, exist_ok=True)

            # Copy audio and transcript if probability_difference is greater than threshold
            if probability_difference > args.probability_difference_threshold:
                shutil.copy(audio_path, output_audio_path)
                shutil.copy(transcript_path, output_transcript_path)
                retained_count += 1
            else:
                # Log the rejected audio path and probability difference
                with open(log_file_path, 'a') as log_file:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    log_file.write(f"[{timestamp}] Rejected: {audio_path} (Difference: {probability_difference})\n")
                rejected_count += 1

        # Write stats for the last book
        write_book_stats(current_book)

if __name__ == "__main__":
    args = parser.parse_args()
    main(args)
