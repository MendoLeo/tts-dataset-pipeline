#!/bin/sh
json_dir="/content/drive/MyDrive/Ewondo/json_files"
audio_dir="/content/drive/MyDrive/Ewondo/Ewondo_NT_audio/wavs_16"
output_dir="/content/drive/MyDrive/Clean"

books="GEN EXO LEV NUM DEU JOS JDG RUT 1SA 2SA 1KI 2KI 1CH 2CH EZR NEH EST JOB PSA PRO ECC SNG ISA JER LAM EZK DAN HOS JOL AMO OBA JON MIC NAM HAB ZEP HAG ZEC MAL MAT MRK LUK JHN ACT ROM 1CO 2CO GAL EPH PHP COL 1TH 2TH 1TI 2TI TIT PHM HEB JAS 1PE 2PE 1JN 2JN 3JN JUD REV"

for book in $books; do
   python segmentation.py --json_path $json_dir/$book.json --audio_dir $audio_dir/$book --output_dir $output_dir
done
