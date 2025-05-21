#!/bin/bash

# Function to display help
usage() {
    echo "Usage: $0 -a <audio_dir> -o <output_dir> [-b <books>] [-t <threshold>] [-l <language>] [-s <batch_size>] [-B] [-h]"
    echo "  -a <audio_dir>     : Directory containing segmented audio files."
    echo "  -o <output_dir>    : Output directory for the filtered segments."
    echo "  -t <threshold>     : Threshold to remove poor alignments (default: -0.2)."
    echo "  -b <books>         : List of books to process (default: all books)."
    echo "  -l <language>      : ISO language code."
    echo "  -s <batch_size>    : Batch size for batch filtering (default: 16)."
    echo "  -B                 : Enable batch filtering mode."
    echo "  -h                 : Show this help message."
    exit 1
}

# Default values
audio_dir=""
output_dir=""
threshold=-0.2
language=""
batch_size=16
batched=false

# Default list of books (entire Bible)
books="GEN EXO LEV NUM DEU JOS JDG RUT 1SA 2SA 1KI 2KI 1CH 2CH EZR NEH EST JOB PSA PRO ECC SNG ISA JER LAM EZK DAN HOS JOL AMO OBA JON MIC NAM HAB ZEP HAG ZEC MAL MAT MRK LUK JHN ACT ROM 1CO 2CO GAL EPH PHP COL 1TH 2TH 1TI 2TI TIT PHM HEB JAS 1PE 2PE 1JN 2JN 3JN JUD REV"

# Parse command-line options
while getopts "a:o:t:b:l:s:Bh" opt; do
    case $opt in
        a) audio_dir="$OPTARG" ;;    # Input audio directory
        o) output_dir="$OPTARG" ;;   # Output directory
        t) threshold="$OPTARG" ;;    # Alignment score threshold
        b) books="$OPTARG" ;;        # Specific books to process
        l) language="$OPTARG" ;;     # ISO language code
        s) batch_size="$OPTARG" ;;   # Batch size for filtering
        B) batched=true ;;           # Enable batched mode
        h) usage ;;                  # Show help
        *) usage ;;                  # Default to help on unknown option
    esac
done

# Check for required parameters
if [ -z "$audio_dir" ] || [ -z "$output_dir" ]; then
    echo "Error: audio_dir and output_dir are required."
    usage
fi

# Check that input and output directories exist
if [ ! -d "$audio_dir" ]; then
    echo "Error: Input audio directory '$audio_dir' does not exist."
    exit 1
fi

if [ ! -d "$output_dir" ]; then
    echo "Error: Output directory '$output_dir' does not exist."
    exit 1
fi

# Loop over each book
for book in $books; do
    audio_folder="$audio_dir/$book"

    # Skip if the book's audio folder doesn't exist
    if [ ! -d "$audio_folder" ]; then
        echo "Warning: Audio directory for '$book' does not exist. Skipping."
        continue
    fi

    echo "Filtering book '$book'..."

    # Build the Python command dynamically
    cmd=(python3 ../run_filter.py \
        --audio_dir "$audio_folder" \
        --output_dir "$output_dir/$book" \
        --probability_difference_threshold "$threshold" \
        --language "$language")

    # Add optional arguments if specified
    $batched && cmd+=(--batched)
    [ -n "$batch_size" ] && cmd+=(--batch_size "$batch_size")

    # Execute the command
    "${cmd[@]}"

    # Check command result
    if [ $? -eq 0 ]; then
        echo "Filtering succeeded for '$book'."
    else
        echo "Error during filtering of '$book'."
    fi
done

echo "Processing completed."
