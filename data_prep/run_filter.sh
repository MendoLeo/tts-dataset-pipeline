#!/bin/sh
audio_dir="/content/drive/MyDrive/Clean" # segment audio aligned path with corresponding text with the same name
output_dir="/content/drive/MyDrive/Clean_filtered" # path to filtered segment


books="GEN EXO LEV NUM DEU JOS JDG RUT 1SA 2SA 1KI 2KI 1CH 2CH EZR NEH EST JOB PSA PRO ECC SNG ISA JER LAM EZK DAN HOS JOL AMO OBA JON MIC NAM HAB ZEP HAG ZEC MAL MAT MRK LUK JHN ACT ROM 1CO 2CO GAL EPH PHP COL 1TH 2TH 1TI 2TI TIT PHM HEB JAS 1PE 2PE 1JN 2JN 3JN JUD REV"
for book in $books; do
   python3 run_filter.py --audio_dir $audio_dir/$book --output_dir $output_dir 
done
