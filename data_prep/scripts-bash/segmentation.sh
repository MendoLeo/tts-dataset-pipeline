#!/bin/bash

# Function to display help
usage() {
    echo "Usage: $0 -j <json_dir> -a <audio_dir> -o <output_dir> [-c <chunk_size>] [-b <books>] [-l <language>] [-h]"
    echo "  -j <json_dir>      : Directory containing the JSON files."
    echo "  -a <audio_dir>     : Directory containing the audio files."
    echo "  -o <output_dir>    : Output directory for processed files."
    echo "  -c <chunk_size>    : Chunk size in seconds (default: 15)."
    echo "  -b <books>         : List of books to process (default: all books)."
    echo "  -l <language>      : Language ISO 639-3 code (e.g., eng, fra, swa)."
    echo "  -h                 : Display this help message."
    exit 1
}

# Default values
json_dir=""
audio_dir=""
output_dir=""
chunk_size=15
language=""
books="GEN EXO LEV NUM DEU JOS JDG RUT 1SA 2SA 1KI 2KI 1CH 2CH EZR NEH EST JOB PSA PRO ECC SNG ISA JER LAM EZK DAN HOS JOL AMO OBA JON MIC NAM HAB ZEP HAG ZEC MAL MAT MRK LUK JHN ACT ROM 1CO 2CO GAL EPH PHP COL 1TH 2TH 1TI 2TI TIT PHM HEB JAS 1PE 2PE 1JN 2JN 3JN JUD REV"

# Parse arguments
while getopts "j:a:o:c:b:l:h" opt; do
    case $opt in
        j) json_dir="$OPTARG" ;;
        a) audio_dir="$OPTARG" ;;
        o) output_dir="$OPTARG" ;;
        c) chunk_size="$OPTARG" ;;
        b) books="$OPTARG" ;;
        l) language="$OPTARG" ;;
        h) usage ;;
        *) usage ;;
    esac
done

# Check for required parameters
if [ -z "$json_dir" ] || [ -z "$audio_dir" ] || [ -z "$output_dir" ]; then
    echo "Error: json_dir, audio_dir, and output_dir are required."
    usage
fi

# Check if input directories exist
for dir in "$json_dir" "$audio_dir"; do
    if [ ! -d "$dir" ]; then
        echo "Error: Directory '$dir' does not exist."
        exit 1
    fi
done

# Create output directory if it doesn't exist
if [ ! -d "$output_dir" ]; then
    echo "Creating output directory '$output_dir'..."
    mkdir -p "$output_dir"
fi

# Check if the Python segmentation script exists
if [ ! -f ../segmentation.py ]; then
    echo "Error: Python script '../segmentation.py' not found."
    exit 1
fi

# Process each book
for book in $books; do
    json_file="$json_dir/$book.json"
    audio_folder="$audio_dir/$book"

    if [ ! -f "$json_file" ]; then
        echo "Warning: JSON missing for '$book'. Skipping."
        continue
    fi

    if [ ! -d "$audio_folder" ]; then
        echo "Warning: Audio missing for '$book'. Skipping."
        continue
    fi

    echo "Processing book '$book'..."
    python3 ../segmentation.py \
        --json_path "$json_file" \
        --audio_dir "$audio_folder" \
        --output_dir "$output_dir/$book" \
        --chunk_size "$chunk_size" \
        --language "$language"

    if [ $? -eq 0 ]; then
        echo "✅ Successfully processed '$book'."
    else
        echo "❌ Error while processing '$book'."
    fi
done

echo "🎉 Processing completed."
