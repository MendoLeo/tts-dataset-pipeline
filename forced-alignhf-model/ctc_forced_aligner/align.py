import json
from pydub import AudioSegment
import torch
from pathlib import Path

from alignment_utils import (
    generate_emissions,
    get_alignments,
    get_spans,
    load_alignment_model,
    load_audio,
)
from text_utils import postprocess_results, preprocess_text

TORCH_DTYPES = {
    "bfloat16": torch.bfloat16,
    "float16": torch.float16,
    "float32": torch.float32,
}

def cli():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--audio_path", help="Path of the audio file", required=True)
    parser.add_argument("--text_path", help="Path of the text to be aligned", required=True)
    parser.add_argument("--output_dir", help="Directory to save output segments", required=True)
    parser.add_argument("--language", type=str, default=None, help="Language in ISO 639-3 code.")
    parser.add_argument("--romanize", action="store_true", default=False, help="Enable romanization for non-latin scripts.")
    parser.add_argument("--split_size", type=str, default="word", choices=["sentence", "word", "char"], help="Alignment level.")
    parser.add_argument("--star_frequency", type=str, default="edges", choices=["segment", "edges"], help="Frequency of <star> token.")
    parser.add_argument("--merge_threshold", type=float, default=0.00, help="Merge segments closer than this threshold.")
    parser.add_argument("--alignment_model", default="MahmoudAshraf/mms-300m-1130-forced-aligner", help="CTC model name for alignment.")
    parser.add_argument("--compute_dtype", type=str, default="float16" if torch.cuda.is_available() else "float32", choices=["bfloat16", "float16", "float32"], help="Compute dtype for alignment inference.")
    parser.add_argument("--batch_size", type=int, default=4, help="Batch size for inference.")
    parser.add_argument("--window_size", type=int, default=30, help="Window size in seconds to chunk the audio.")
    parser.add_argument("--context_size", type=int, default=2, help="Overlap between chunks in seconds.")
    parser.add_argument("--attn_implementation", type=str, default=None, choices=["eager", "sdpa", "flash_attention_2", None], help="Attention implementation for the model.")
    parser.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu", help="Device for execution ('cuda' or 'cpu').")
    parser.add_argument("--segment_audio", action="store_true", help="Enable segmentation of audio based on timestamps.")
    parser.add_argument("--generate_json", action="store_true", help="Enable generation of JSON file with results.")
    parser.add_argument("--generate_txt", action="store_true", help="Enable generation of TXT file with results.")

    args = parser.parse_args()

    model, tokenizer = load_alignment_model(
        args.device,
        args.alignment_model,
        args.attn_implementation,
        TORCH_DTYPES[args.compute_dtype],
    )

    audio_waveform = load_audio(args.audio_path, model.dtype, model.device)
    emissions, stride = generate_emissions(
        model, audio_waveform, args.window_size, args.context_size, args.batch_size
    )



    with open(args.text_path, "r", encoding="utf-8") as f:
        text = f.read().replace("\n", " ").strip()

    # includ bible verse loading after applying load_json function
    

    tokens_starred, text_starred = preprocess_text(
        text, args.romanize, args.language, args.split_size, args.star_frequency
    )

    segments, scores, blank_token = get_alignments(
        emissions,
        tokens_starred,
        tokenizer,
    )

    spans = get_spans(tokens_starred, segments, blank_token)

    results = postprocess_results(
        text_starred, spans, stride, scores, args.merge_threshold
    )

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    txt_output_path = output_dir / f"{Path(args.audio_path).stem}.txt"
    json_output_path = output_dir / f"{Path(args.audio_path).stem}.json"

    # Générer le fichier TXT si demandé
    if args.generate_txt:
        with open(txt_output_path, "w", encoding="utf-8") as f:
            for result in results:
                f.write(f"{result['start']}-{result['end']}: {result['text']}\n")

    # Générer le fichier JSON si demandé
    if args.generate_json:
        with open(json_output_path, "w", encoding="utf-8") as f:
            json.dump({"text": text, "segments": results}, f, indent=4)

    # Segmentation audio si demandé
    if args.segment_audio:
        audio = AudioSegment.from_file(args.audio_path, format="wav")
        for i, result in enumerate(results):
            start_ms = int(result['start'] * 1000)
            end_ms = int(result['end'] * 1000)

            # Vérification que les timestamps sont valides
            if start_ms < end_ms:
                filename = f"{Path(args.audio_path).stem}_{str(i+1).zfill(3)}"
                audio_path = (output_dir / filename).with_suffix(".wav")
                segment = audio[start_ms:end_ms]
                segment.export(audio_path, format="wav")

                transcript_path = (output_dir / filename).with_suffix(".txt")
                with open(transcript_path, "w", encoding="utf-8") as f:
                    f.write(result['text'])

if __name__ == "__main__":
    cli()
