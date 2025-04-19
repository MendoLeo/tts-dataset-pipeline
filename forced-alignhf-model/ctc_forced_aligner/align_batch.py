import os
import subprocess
from tqdm import tqdm
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="Batch align audio-text pairs using align_p.py")

    parser.add_argument('--audio_dir', required=True, help="Directory containing audio files (.wav)")
    parser.add_argument('--text_dir', required=True, help="Directory containing text files (.txt)")
    parser.add_argument('--output_dir', required=True, help="Directory to save aligned output")
    parser.add_argument('--language', default='fr', help="Language code (e.g., fr, bum)")
    parser.add_argument('--split_size', default='word', help="Split size: sentence, word, or char")
    parser.add_argument('--romanize', action='store_true', help="Enable romanization")
    parser.add_argument('--alignment_model', default='MahmoudAshraf/mms-300m-1130-forced-aligner')
    parser.add_argument('--compute_dtype', default='float16')
    parser.add_argument('--batch_size', default='4')
    parser.add_argument('--window_size', default='30')
    parser.add_argument('--context_size', default='2')
    parser.add_argument('--attn_implementation', default=None)
    parser.add_argument('--device', default='cuda')
    parser.add_argument('--segment_audio', action='store_true', help="Enable audio segmentation")
    parser.add_argument('--generate_json', action='store_true', help="Generate .json output")
    parser.add_argument('--generate_txt', action='store_true', help="Generate .txt output")

    return parser.parse_args()

def main():
    args = parse_args()

    audio_files = [f for f in os.listdir(args.audio_dir) if f.endswith('.wav')]
    audio_files.sort()

    for audio in tqdm(audio_files, desc="Aligning files", unit="file"):
        audio_path = os.path.join(args.audio_dir, audio)
        text_path = os.path.join(args.text_dir, audio.replace('.wav', '.txt'))

        if not os.path.exists(text_path):
            print(f"[⚠️] Text file not found for {audio}")
            continue

        cmd = [
            "python", "align_p.py",
            "--audio_path", audio_path,
            "--text_path", text_path,
            "--output_dir", args.output_dir,
            "--language", args.language,
            "--split_size", args.split_size,
            "--alignment_model", args.alignment_model,
            "--compute_dtype", args.compute_dtype,
            "--batch_size", str(args.batch_size),
            "--window_size", str(args.window_size),
            "--context_size", str(args.context_size),
            "--device", args.device
        ]

        if args.romanize:
            cmd.append("--romanize")
        if args.segment_audio:
            cmd.append("--segment_audio")
        if args.generate_json:
            cmd.append("--generate_json")
        if args.generate_txt:
            cmd.append("--generate_txt")
        if args.attn_implementation:
            cmd.extend(["--attn_implementation", args.attn_implementation])

        subprocess.run(cmd)

if __name__ == "__main__":
    main()
