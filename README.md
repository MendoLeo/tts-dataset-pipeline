# 🧐 TTS & ASR Dataset Pipeline


An open-source pipeline designed to simplify the creation of datasets for Text-to-Speech (TTS) and Automatic Speech Recognition (ASR), supporting both specific (biblical) and generic (any corpus/language) use cases.

---

## 📌 Table of Contents

1. [🎯 Motivation & Inspirations](#-motivation--inspirations)  
2. [🧠 Pipeline Architecture](#-pipeline-architecture)  
3. [📚 Use Cases](#-use-cases)  
4. [⚙️ Installation](#-installation)  
5. [🧾 Data Preparation](#-data-preparation)  
6. [⚙️ Common Preprocessing Steps](#-common-preprocessing-steps)  
7. [📖 Biblical Case](#-biblical-case)  
8. [🌍 Generic Case](#-generic-case)  
9. [🙌 Contributing](#-contributing)  
10. [📄 License](#-license)

---

## 🎯 Motivation & Inspirations


This project was born out of a desire to expand access to speech technologies for all languages, especially **low-resource languages**.  
Inspired by Meta AI’s **Massively Multilingual Speech (MMS)** project, this open-source pipeline aims to make TTS/ASR dataset creation easier by providing a full set of tools for:

- preprocessing text and audio data,
- automatic alignment,
- data filtering and formatting.

---

## 🧠 Pipeline Architecture

```
Raw Data (audio/text)
      │
      ▼
Preprocessing (conversion + cleaning)
      │
      ▼
Text-audio alignment
      │
      ▼
Alignment filtering
      │
      ▼
Final formatting (CSV, JSON, etc.)
```

---

## 📚 Use Cases

This pipeline supports **two main scenarios**:

- 📖 **Biblical case**: Texts from scriptures or other books, often structured using book,chapter,verse segmentation.
- 🌍 **Generic case**: Any data with transcription and audio (podcasts, stories, interviews, etc.).

---

## ⚙️ Installation

```bash
# 1. Clone the repository
git clone https://github.com/MendoLeo/tts-dataset-pipeline.git
cd tts-dataset-pipeline

# 2. Install Python dependencies
pip install -r requirements.txt
```

### 📌 C++ Alignment Dependency (Generic case only)

```bash
cd forced-alignhf-model
pip install pybind11
python setup.py build_ext --inplace
```

> ⚠️ Requirements: Python 3.10, `pybind11`, and a C++ compiler (`g++` recommended)

---

## 🧾 Data Preparation

### 📖 Biblical Data

This case is inspired by [OpenBible](https://github.com/bookbot-hive/OpenBible-TTShttps://github.com/bookbot-hive/OpenBible-TTS) work

- Required format: structure transcripts on `.json` file format:
  ```json
  [
      {
          "numVerset": "MAT.1.1",
          "verset": "Kalate éndane Yésus Krist, e mona David, e mon Abraham."
      },
      {
          "numVerset": "MAT.1.2",
          "verset": "Abraham a nga biaé Izak, Izak a nga biaé Yakob, Yakob a nga biaé Yuda baa be bobenyañ. "
      },
      {
          "numVerset": "MAT.1.3",
          "verset": "Yuda a nga biaé Farés a Zara aluʼu baa Tamar. Farés a nga biaé Esrôm, Esrôm a nga biaé Aram. "
      },
      {
          "numVerset": "MAT.1.4",
          "verset": "Aram a nga biaé Aminadab, Aminadab ke a biaé Naasôn. Naasôn ke a biaé Salmôn. "
      },
  ]
  ```
  Examples of these JSON files can be found in the [Drive](https://drive.google.com/drive/folders/1mq9C3AQU0J5xAwwUfWQDwoTnbH6OYi3G) as for more than 26 cameroonian dialects Bible transcripts (good starter to build your own dataset, check if your dialect is [available](https://docs.google.com/spreadsheets/d/1m2badLeGIzfrhetIE0BpXamtGAWBhvEP/edit?usp=drive_web&ouid=107335318586372564034&rtpof=true).


- Structure:
  ```
  ├── audio_dir/
    ├── MAT
      ├── MAT_001.wav
      ├── MAT_002.wav
      ├── MAT_003.wav
    ├── 1CO
    ...
  ├── transcripts/
    ├── MAT.json
    ├── PSA.json
    ├── GEN.json
    ├── REV.json
    ...
    ```

### 🌍 Generic Data

- Required format: free-form transcription `.txt`
- Structure:
  ```
  ├── text_dir/
    ├── AV1.txt
    ├── AV2.txt

  ├── audio_dir/
    ├── AV1.wav
    ├── AV2.wav
  ```
  ---

AV1.txt must contain text to align with audio as:

  ```
  친구들과 함께 공원에 가기로 했다.
  우리는 자전거를 타고, 길을 따라 천천히 달렸다
  공원에 도착하니 사람들이 많이 있었다.
  아이들이 놀이터에서 놀고, 어른들은 산책을 하고 있었다

  ```

## ⚙️ Common Preprocessing Steps

```bash
 cd data_prep
```

### 🔄 Audio Conversion

Convert audio files to:
- `wav` 16kHz
- `wav` 22kHz
- `wav` 44kHz

  ```bash
    python convert_audio.py \
      --audio_dir ./audio_files \
      --sample 16000 \ 
      --output_dir wav_output

  ```

### 🔇 Audio Denoising

Automatically removes background noise or unwanted music.

  ```bash
    python denoising.py \ 
      --src_path /noised/audios \ 
      --output_dir /denoised/audios
  ```

---

## 📖 Biblical Case

### 📌 Alignment

- **Align single book:**
  ```bash
    python run_segmentation.py \
      --json_path /transcripts/json-file/PSA.json \
      --audio_dir /audio_dir/PSA \
      --output_dir /outputs/PSA \
      --language 'bum' \
      --chunk_size_s 15
    ```

which will generate:

```
outputs/PSA/
├── PSA_001
│   ├── PSA_001_001.txt
│   ├── PSA_001_001.wav
│   ├── PSA_001_002.txt
│   ├── PSA_001_002.wav
│   ├── ...
├── PSA_002
│   ├── PSA_002_001.txt
│   ├── PSA_002_001.wav
│   ├── PSA_002_002.txt
│   ├── PSA_002_002.wav
├── ...
...
```
- **Align multiple books:**
  ```bash
    cd scripts-bash
    segmentation.sh -j /to/json_files -a /to/audio_files -o /to/output_dir -b "GEN EXO PSA" -c 15

  ```

### 🧹 Filtering

#### Arguments

| Argument | Description | Default |
|---|---|---|
| `--audio_path` | Path to the audio and transcript file with the same name | Required |
| `--language` | Language in ISO 639-3 code | Required |
| `--chunck_size` | Chunk size in seconds | 15 seconds as in mms |
| `--probability_difference_threshold` | threshold for bad alignment removing | -0.2 as in mms project |

- **Filter single book:**
  ```bash
    python run_filter.py \
    --audio_dir /aligned/GEN/ \
    --output_dir /output/filtered \
    --language 'bum' \
    --chunk_size_s 15 \
    --probability_difference_threshold -0.2
  ```
- **Filter multiple books:**

  ```bash
    cd scripts-bash
    run_filter.sh -a /path/to/audio_files -o /path/to/output_dir -b "GEN EXO PSA" -t -0.3

  ```

---

## 🌍 Generic Case

### 🔧 Alignment Setup

This case uses a CTC model implemented in C++ by [Mohamoud Ashraf](https://github.com/MahmoudAshraf97/ctc-forced-aligner/tree/main) with integration via `pybind11`.

### 🔁 Alignment

#### Arguments


| Argument | Description | Default |
|---|---|---|
| `--audio_path` | Path to the audio file | Required |
| `--text_path` | Path to the text file | Required |
| `--language` | Language in ISO 639-3 code | Required |
| `--romanize` | Enable romanization for non-latin scripts or for multilingual models regardless of the language, required when using the default model| False |
| `--split_size` | Alignment granularity: "sentence", "word", or "char" | "word" |
| `--star_frequency` | Frequency of `<star>` token: "segment" or "edges" | "edges" |
| `--merge_threshold` | Merge threshold for segment merging | 0.00 |
| `--alignment_model` | Name of the alignment model | [MahmoudAshraf/mms-300m-1130-forced-aligner](https://huggingface.co/MahmoudAshraf/mms-300m-1130-forced-aligner) |
| `--compute_dtype` | Compute dtype for inference | "float32" |
| `--batch_size` | Batch size for inference | 4 |
| `--window_size` | Window size in seconds for audio chunking | 30 |
| `--context_size` | Overlap between chunks in seconds | 2 |
| `--attn_implementation` | Attention implementation | "eager" |
| `--device` | Device to use for inference: "cuda" or "cpu" | "cuda" if available, else "cpu" |
| `--generate_txt` | Define if you want text file with timestamp and text alignment |False|
| `--generate_json` | Define if you want text with timestamp and alignment score|False|






```bash
  cd forced-alignhf-model/ctc_forced_aligner

  python align_batch.py \
      --audio_dir "/content/tts-dataset-pipeline/data/audios" \
      --text_dir "/content/tts-dataset-pipeline/data/transcripts" \
      --output_dir "/content/sample_data/pipeline-align" \
      --language "bum" \
      --romanize \
      --segment_audio \
      --generate_txt \
      --split_size "sentence"
```

- **Optional:** Bash script alignment (serial or parallel)

```bash
   align_batch_launcher.sh \
      --audio_dir "/content/tts-dataset-pipeline/data/audios" \
      --text_dir "/content/tts-dataset-pipeline/data/transcripts" \
      --output_dir "/content/sample_data/pipeline" \
      --language "bum" \
      --romanize \
      --segment_audio \
      --generate_txt \
      --split_size "sentence"
```

### 🧹 Generic Filtering

```bash
    cd data_prep
    python generic_filter.py \
      --audio_dir /path/to/align/data \
      --output_dir /path/to/cleaned/alignment \
      --language "bum" \
      --probability_difference_threshold -0.25 \
  ```

---

## 🙌 Contributing

You can:

- Report a bug or suggest a feature
- Submit a PR with local language use cases
- Add a new language (locale, test sets, etc.)
- Translate this README into your language

---

## 📄 License

This project incorporates components and resources licensed under different open-source and open-content licenses:

- 🧩 Parts of the **code** are licensed under the [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0).
- 🧱 Some elements are licensed under the [BSD 3-Clause License](https://opensource.org/licenses/BSD-3-Clause).
- 📚 Some models are under the [Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)](https://creativecommons.org/licenses/by-nc/4.0/).

Unless otherwise specified in individual files, this repository as a whole is distributed under the: **(CC BY-NC 4.0)** license.


---

## 👏 Acknowledgement

This project would not be possible without the contributions and inspirations from the open-source community and the research teams behind:

- [Massively Multilingual Speech (MMS)](https://github.com/facebookresearch/fairseq/tree/main/examples/mms) by Meta AI
- [Tikeng Notsawo Pascal et al](https://openreview.net/forum?id=Q5ZxoD2LqcI) for their work on building first bible transcript dataset for cameroonian dialects
- [Mohamoud Ashraf](https://github.com/MahmoudAshraf97/ctc-forced-aligner/tree/main) for open sourced his work, where we use timestamp alignemnt to have complet alignment with audio-text generation
- [OpenBible](https://github.com/bookbot-hive/OpenBible-TTShttps://github.com/bookbot-hive/OpenBible-TTS) for open sourced alignment method for bible case that we ameliore text processing to expand to all language also adding denoising and audio conversion
- All contributors who support local language tech
- Users and testers helping improve the pipeline continuously

Thank you for your support and collaboration!

