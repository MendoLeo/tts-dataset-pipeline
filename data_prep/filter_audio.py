from typing import List
from pathlib import Path
import argparse

import numpy as np
import torch
import torchaudio
import torchaudio.transforms as T
from torch.nn.utils.rnn import pad_sequence
from tqdm.auto import tqdm

from data_prep.alignment_utils import MMS_SUBSAMPLING_RATIO,compute_alignment_scores
from text_utils import preprocess_verse

parser = argparse.ArgumentParser()
parser.add_argument(
    "--audio_path",
    required=True,
    help="Path to the audio file. Example: outputs/openbible_swahili/EPH/EPH_003/EPH_003_001.wav",
)
parser.add_argument("--ground_truth", required=True, help="Ground truth text to forced-align with.")
parser.add_argument("--language", type=str, default=None, help="Language in ISO 639-3 code.")
parser.add_argument("--chunk_size_s", type=int, default=15, help="Chunk size in seconds")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# load MMS aligner model
bundle = torchaudio.pipelines.MMS_FA
model = bundle.get_model(with_star=True).to(device)
DICTIONARY = bundle.get_dict()


def compute_probability_difference(audio_path: str, ground_truth: str,language: str, chunk_size_s: int = 15) -> float:
    audio_path = Path(audio_path)

    # apply preprocessing
    # verse = preprocess_verse(ground_truth)

    verse = preprocess_verse(ground_truth,language)
    words = verse.split()

    # load audio
    input_waveform, input_sample_rate = torchaudio.load(audio_path)
    resampler = T.Resample(input_sample_rate, bundle.sample_rate, dtype=input_waveform.dtype)
    resampled_waveform = resampler(input_waveform)
    # split audio into chunks to avoid OOM and faster inference
    chunk_size_frames = chunk_size_s * bundle.sample_rate
    chunks = [
        resampled_waveform[:, i : i + chunk_size_frames]
        for i in range(0, resampled_waveform.shape[1], chunk_size_frames)
    ]

    # collect per-chunk emissions, rejoin
    emissions = []
    with torch.inference_mode():
        for chunk in chunks:
            # NOTE: we could pad here, but it'll need to be removed later
            # skipping for simplicity, since it's at most 25ms
            if chunk.size(1) >= MMS_SUBSAMPLING_RATIO:
                emission, _ = model(chunk.to(device))  # (1, chunk_frame_length, num_labels)
                emissions.append(emission)

    emission = torch.cat(emissions, dim=1)  # (1, frame_length, num_labels)
    num_frames = emission.size(1)
    assert len(DICTIONARY) == emission.shape[2]

    # method proposed in §3.1.5 of MMS paper: https://arxiv.org/abs/2305.13516
    # \frac{1}{T} \log P(Y_{aligned} | X) - \log P(Y_{greedy} | X)

    # compute greedy search score
    probs = torch.softmax(emission, dim=-1)  # (1, frame_length, num_labels)
    greedy_probs = torch.max(probs, dim=-1).values.squeeze()  # (1, frame_length)
    greedy_log_probs = torch.sum(torch.log(greedy_probs)).cpu().numpy().item()  # (1)

    # compute forced-alignment score
    aligned_probs = compute_alignment_scores(emission, words, DICTIONARY, device)  # (1, frame_length)
    aligned_log_probs = torch.sum(torch.log(aligned_probs)).cpu().numpy().item()  # (1)
    if aligned_log_probs == -np.inf:
        print(f"Alignment failed for {audio_path}.")

    # compute length-normalized probability difference
    probability_diff = (aligned_log_probs - greedy_log_probs) / num_frames

    return probability_diff


def compute_probability_difference_batched(
    audio_paths: List[Path], ground_truths: List[str], language:str, batch_size: int = 16
) -> List[float]:
    # apply preprocessing
   
    # verses = [preprocess_verse(v) for v in ground_truths]

    verses = [preprocess_verse(v,language) for v in ground_truths]
    words = [verse.split() for verse in verses]
    # batch transcripts
    words_batches = [words[i : i + batch_size] for i in range(0, len(words), batch_size)]

    # load audio
    waveforms = [torchaudio.load(audio_path) for audio_path in audio_paths]

    input_waveform, input_sample_rate = waveforms[0]
    resampler = T.Resample(input_sample_rate, bundle.sample_rate, dtype=input_waveform.dtype)
    resampled_waveforms = [resampler(waveform).squeeze() for (waveform, _) in waveforms]

    # store waveform lengths for padding
    waveform_lengths = [waveform.shape[0] for waveform in resampled_waveforms]
    # batch waveforms and lengths
    waveform_lengths_batches = [
        torch.tensor(waveform_lengths[i : i + batch_size], dtype=torch.int64)
        for i in range(0, len(waveform_lengths), batch_size)
    ]
    waveforms_batches = [
        pad_sequence(
            resampled_waveforms[i : i + batch_size], batch_first=True, padding_value=0
        )  # (batch_size, max_batch_frame_length)
        for i in range(0, len(resampled_waveforms), batch_size)
    ]
    assert len(waveforms_batches) == len(waveform_lengths_batches) == len(words_batches)

    # collect per-batch probability differences
    probability_diffs = []
    for waveform_batch, waveform_lengths_batch, words_batch in tqdm(
        zip(waveforms_batches, waveform_lengths_batches, words_batches), total=len(waveforms_batches)
    ):
        with torch.inference_mode():
            emission, lengths = model(
                waveform_batch.to(device), waveform_lengths_batch.to(device)
            )  # (batch_size, max_batch_frame_length, num_labels)

        assert len(DICTIONARY) == emission.shape[2]

        greedy_log_probs, aligned_log_probs = [], []

        # method proposed in §3.1.5 of MMS paper: https://arxiv.org/abs/2305.13516
        # \frac{1}{T} \log P(Y_{aligned} | X) - \log P(Y_{greedy} | X)

        # compute greedy search score
        for i, length in zip(range(len(waveform_batch)), lengths):
            prob = torch.softmax(emission[i, :length, :].unsqueeze(dim=0), dim=-1)  # (1, frame_length, num_labels)
            greedy_prob = torch.max(prob, dim=-1).values  # (1, frame_length)
            greedy_log_prob = torch.sum(torch.log(greedy_prob), dim=-1).cpu().numpy().item()  # (1,)
            greedy_log_probs.append(greedy_log_prob)

        # compute forced-alignment score
        for i, length, words in zip(range(len(waveform_batch)), lengths, words_batch):
            aligned_prob = compute_alignment_scores(
                emission[i, :length, :].unsqueeze(dim=0), words, DICTIONARY, device
            ).squeeze()  # (1, max_batch_frame_length)
            aligned_log_prob = torch.sum(torch.log(aligned_prob), dim=-1).cpu().numpy().item()  # (1,)
            aligned_log_probs.append(aligned_log_prob)

        # compute length-normalized probability difference
        probability_diff = (np.array(aligned_log_probs) - np.array(greedy_log_probs)) / lengths.cpu().numpy()
        probability_diffs.append(probability_diff)

    probability_diffs = np.concatenate(probability_diffs).tolist()
    return probability_diffs


if __name__ == "__main__":
    args = parser.parse_args()
    probability_difference = compute_probability_difference(args.audio_path, args.ground_truth,args.language, args.chunk_size_s)
    print(probability_difference)
