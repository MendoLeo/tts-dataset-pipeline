#!/bin/bash

# Script shell to align audio-text with options --argument
# Execution Eg. : ./script_bash.sh --audio_dir "/path/to/audio" --text_dir "/path/to/text" --output_dir "/path/to/output" --language "en" --split_size "sentence"

# Fonction pour afficher l'usage
usage() {
    echo "Usage: $0 --audio_dir <audio_dir> --text_dir <text_dir> --output_dir <output_dir> [options]"
    echo "Options:"
    echo "  --audio_dir <path>        Directory containing audio files"
    echo "  --text_dir <path>         Directory containing text files"
    echo "  --output_dir <path>       Directory to save output segments"
    echo "  --language <lang>         Language (default: fr)"
    echo "  --split_size <size>       Split size: sentence, word, or char (default: word)"
    echo "  --romanize                Enable romanization (default: false)"
    echo "  --alignment_model <name>  Alignment model (default: MahmoudAshraf/mms-300m-1130-forced-aligner)"
    echo "  --compute_dtype <dtype>   Compute dtype (default: float16)"
    echo "  --batch_size <int>        Batch size for inference (default: 4)"
    echo "  --window_size <int>       Window size in seconds (default: 30)"
    echo "  --context_size <int>      Overlap between chunks in seconds (default: 2)"
    echo "  --attn_implementation <type> Attention implementation (default: None)"
    echo "  --device <cpu/cuda>       Device for execution (default: auto-detect)"
    echo "  --segment_audio           Enable segmentation of the audio (default: true)"
    echo "  --generate_json           Enable JSON output (default: true)"
    echo "  --generate_txt            Enable TXT output (default: true)"
    exit 1
}

# Parsing les arguments
while [[ "$#" -gt 0 ]]; do
    case "$1" in
        --audio_dir) audio_dir="$2"; shift 2 ;;
        --text_dir) text_dir="$2"; shift 2 ;;
        --output_dir) output_dir="$2"; shift 2 ;;
        --language) language="$2"; shift 2 ;;
        --split_size) split_size="$2"; shift 2 ;;
        --romanize) romanize=true; shift 1 ;;
        --alignment_model) alignment_model="$2"; shift 2 ;;
        --compute_dtype) compute_dtype="$2"; shift 2 ;;
        --batch_size) batch_size="$2"; shift 2 ;;
        --window_size) window_size="$2"; shift 2 ;;
        --context_size) context_size="$2"; shift 2 ;;
        --attn_implementation) attn_implementation="$2"; shift 2 ;;
        --device) device="$2"; shift 2 ;;
        --segment_audio) segment_audio=true; shift 1 ;;
        --generate_json) generate_json=true; shift 1 ;;
        --generate_txt) generate_txt=true; shift 1 ;;
        *) echo "Unknown option: $1"; usage ;;
    esac
done

# Valeurs par défaut si non spécifiées
language="${language:-fr}"
split_size="${split_size:-word}"
romanize="${romanize:-false}"
alignment_model="${alignment_model:-MahmoudAshraf/mms-300m-1130-forced-aligner}"
compute_dtype="${compute_dtype:-float16}"
batch_size="${batch_size:-4}"
window_size="${window_size:-30}"
context_size="${context_size:-2}"
device="${device:-$(if [[ $(command -v nvidia-smi) ]]; then echo "cuda"; else echo "cpu"; fi)}"
segment_audio="${segment_audio:-true}"
generate_json="${generate_json:-true}"
generate_txt="${generate_txt:-true}"

# Flags d'option conditionnels
attn_implementation_flag=""
[ -n "$attn_implementation" ] && attn_implementation_flag="--attn_implementation $attn_implementation"

romanize_flag=""
segment_audio_flag=""
generate_json_flag=""
generate_txt_flag=""

[ "$romanize" == "true" ] && romanize_flag="--romanize"
[ "$segment_audio" == "true" ] && segment_audio_flag="--segment_audio"
[ "$generate_json" == "true" ] && generate_json_flag="--generate_json"
[ "$generate_txt" == "true" ] && generate_txt_flag="--generate_txt"

# Vérifier que les répertoires sont définis
if [ -z "$audio_dir" ] || [ -z "$text_dir" ] || [ -z "$output_dir" ]; then
    echo "Error: audio_dir, text_dir, and output_dir are required."
    usage
fi

# Lancer le script Python pour chaque fichier
for audio_file in "$audio_dir"/*.wav; do
    text_file="$text_dir/$(basename "$audio_file" .wav).txt"
    
    if [ -f "$text_file" ]; then
        echo "Processing: $audio_file with $text_file"
        python align_p.py \
            --audio_path "$audio_file" \
            --text_path "$text_file" \
            --output_dir "$output_dir" \
            --language "$language" \
            --split_size "$split_size" \
            $romanize_flag \
            --alignment_model "$alignment_model" \
            --compute_dtype "$compute_dtype" \
            --batch_size "$batch_size" \
            --window_size "$window_size" \
            --context_size "$context_size" \
            $attn_implementation_flag \
            --device "$device" \
            $segment_audio_flag \
            $generate_json_flag \
            $generate_txt_flag
    else
        echo "Text file for $audio_file not found."
    fi
done
