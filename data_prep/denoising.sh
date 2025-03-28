#!/bin/bash
src_path    = "/home/mendo/Downloads/LM/LM-5/LM-TTS-Main/data_marte_wav/bu-ba-fr-aligned/Output/Bafia/output"
output_dir  = "" # put drive path

# in the case i need to make frmawork, i must handle none bible audios cases(just folder with noising audios)
books="GEN EXO LEV NUM DEU JOS JDG RUT 1SA 2SA 1KI 2KI 1CH 2CH EZR NEH EST JOB PSA PRO ECC SNG ISA JER LAM EZK DAN HOS JOL AMO OBA JON MIC NAM HAB ZEP HAG ZEC MAL MAT MRK LUK JHN ACT ROM 1CO 2CO GAL EPH PHP COL 1TH 2TH 1TI 2TI TIT PHM HEB JAS 1PE 2PE 1JN 2JN 3JN JUD REV"

for book in $books; do 
   echo "Traitement de $book..." 
   python3 denoising.py --src_path $src_path/$book --output_dir $output_dir 
done
