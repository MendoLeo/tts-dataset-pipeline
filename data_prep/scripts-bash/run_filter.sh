#!/bin/bash

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

audio_dir=""
output_dir=""
threshold=-0.2
language=""
batch_size=16
batched=false

books="GEN EXO LEV NUM DEU JOS JDG RUT 1SA 2SA 1KI 2KI 1CH 2CH EZR NEH EST JOB PSA PRO ECC SNG ISA JER LAM EZK DAN HOS JOL AMO OBA JON MIC NAM HAB ZEP HAG ZEC MAL MAT MRK LUK JHN ACT ROM 1CO 2CO GAL EPH PHP COL 1TH 2TH 1TI 2TI TIT PHM HEB JAS 1PE 2PE 1JN 2JN 3JN JUD REV"

while getopts "a:o:t:b:l:s:B:h" opt; do
    case $opt in
        a) audio_dir="$OPTARG" ;;
        o) output_dir="$OPTARG" ;;
        t) threshold="$OPTARG" ;;
        b) books="$OPTARG" ;;
        l) language="$OPTARG" ;;
        s) batch_size="$OPTARG" ;;
        B) batched=true ;;
        h) usage ;;
        *) usage ;;
    esac
done

if [ -z "$audio_dir" ] || [ -z "$output_dir" ]; then
    echo "Error: audio_dir and output_dir are required."
    usage
fi

if [ ! -d "$audio_dir" ]; then
    echo "Error: Input audio directory '$audio_dir' does not exist."
    exit 1
fi

mkdir -p "$output_dir"

for book in $books; do
    audio_folder="$audio_dir/$book"

    if [ ! -d "$audio_folder" ]; then
        echo "Warning: Audio directory for '$book' does not exist. Skipping."
        continue
    fi

    echo "Filtering book '$book'..."

    cmd=(python3 ../run_filter.py \
        --audio_dir "$audio_folder" \
        --output_dir "$output_dir/$book" \
        --log_dir "$output_dir" \
        --probability_difference_threshold "$threshold" \
        --language "$language")

    $batched && cmd+=(--batched)
    [ -n "$batch_size" ] && cmd+=(--batch_size "$batch_size")

    "${cmd[@]}"

    if [ $? -eq 0 ]; then
        echo "Filtering succeeded for '$book'."
    else
        echo "Error during filtering of '$book'."
    fi
done

echo "Processing completed."
