# Mon pipeline

# CTC Forced Aligner

Ce projet utilise un modèle CTC pour l'alignement forcé dans la reconnaissance de la parole. Le module est écrit en C++ et utilise `pybind11` pour l'intégration avec Python.

## Installation

### Pré-requis
- Python 3.x
- `pybind11` pour l'intégration de C++ avec Python (!pip install pybind11)
- Un compilateur C++ (sur Colab, nous utiliserons `g++`)

### Étapes pour installer et utiliser sur un nouvel environnement (ex: Google Colab)

1. **Cloner le dépôt**

   Clonez ce dépôt sur votre environnement local ou dans Colab avec la commande suivante :

   ```bash
   !git clone https://github.com/MendoLeo/tts-dataset-pipeline.git
2. **compiler le module**

    ```bash
    %cd forced-alignhf-model
    !python3 setup.py build_ext --inplace

3. **Launch alignment for txt and audios files**

   ```bash
   !python align_batch.py \
      --audio_dir "/content/tts-dataset-pipeline/data/audios" \
      --text_dir "/content/tts-dataset-pipeline/data/transcripts" \
      --output_dir "/content/sample_data/pipeline-align" \
      --language "bum" \
      --romanize \
      --segment_audio \
      --generate_txt \
      --split_size "sentence"

4. **Launch with bash command**

   ```bash
   bash align_batch_launcher.sh \
      --audio_dir "/content/tts-dataset-pipeline/data/audios" \
      --text_dir "/content/tts-dataset-pipeline/data/transcripts" \
      --output_dir "/content/sample_data/pipeline-align" \
      --language "bum" \
      --romanize \
      --segment_audio \
      --generate_txt \
      --split_size "sentence"

