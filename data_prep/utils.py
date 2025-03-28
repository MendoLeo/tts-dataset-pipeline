import re
import string

from unidecode import unidecode
import unicodedata
import csv
from pathlib import Path
import torch
import torchaudio.functional as F
import torchaudio
from denoiser import pretrained  # Import du modèle pré-entraîné
from denoiser.dsp import convert_audio

#########################################################
# MMS feature extractor minimum input frame size (25ms)
# also the same value as `ratio`
# `ratio = input_waveform.size(1) / num_frames`
#########################################################

MMS_SUBSAMPLING_RATIO = 400

###################
# text utils
###################


def preprocess_verse(text: str) -> str:
    text = unidecode(text)
    text = unicodedata.normalize('NFKC', text)
    text = text.lower()
    text = text.translate(str.maketrans('', '', string.punctuation))
    text = re.sub("\s+", " ", text)
    return text


###############################################################################################################
# functions modified from https://pytorch.org/audio/main/tutorials/ctc_forced_alignment_api_tutorial.html
###############################################################################################################


def align(emission, tokens, device):
    targets = torch.tensor([tokens], dtype=torch.int32, device=device)
    alignments, scores = F.forced_align(emission, targets, blank=0)

    alignments, scores = alignments[0], scores[0]  # remove batch dimension for simplicity
    scores = scores.exp()  # convert back to probability
    return alignments, scores


def unflatten(list_, lengths):
    assert len(list_) == sum(lengths)
    i = 0
    ret = []
    for l in lengths:  # noqa: E741
        ret.append(list_[i : i + l])
        i += l
    return ret


def compute_alignments(emission, transcript, dictionary, device):
    tokens = [dictionary[char] for word in transcript for char in word]
    alignment, scores = align(emission, tokens, device)
    token_spans = F.merge_tokens(alignment, scores)
    word_spans = unflatten(token_spans, [len(word) for word in transcript])
    return word_spans


def compute_alignment_scores(emission, transcript, dictionary, device):
    tokens = [dictionary[char] for word in transcript for char in word]

    try:
        _, scores = align(emission, tokens, device)
        return scores
    except RuntimeError as e:
        # sometimes emission frames are too short for the transcript
        # comparing emission shape and targets length is insufficient due to CTC padding
        if e.args[0].startswith("targets length is too long for CTC"):
            # return 0 probability for this case
            return torch.zeros((1, emission.size(1)), device=device)
        else:
            raise e

######### statistic to controle fitered and rejected verses ############

def write_book_stats(book_name:str,retained_count:int, rejected_count:int,history_file_path:Path):
        """Helper function to write stats to the CSV."""
        if book_name:
            with open(history_file_path, "a", newline="") as history_file:
                csv_writer = csv.writer(history_file)
                csv_writer.writerow([book_name, retained_count, rejected_count])
            retained_count = 0
            rejected_count = 0


############ process audio by denoising(in our case,remove background music) #############

def denoise(audio_path: Path,output_dir:Path) -> str:
    """Dénoise un fichier audio en utilisant le CPU ou le GPU selon la disponibilité."""
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = pretrained.dns64().to(device)

    # Charger et convertir l'audio
    wav, sr = torchaudio.load(audio_path)
    wav = convert_audio(wav, sr, model.sample_rate, model.chin).to(device)

    # Dénoiser
    with torch.no_grad():
        denoised = model(wav[None])[0].cpu()  # Assurez-vous de ramener en CPU pour torchaudio.save

    # Sauvegarde du fichier
    torchaudio.save(output_dir, denoised, model.sample_rate) # quelle frequence pour output audios?
    print(f"Processed and saved: {output_dir}")
    return output_dir