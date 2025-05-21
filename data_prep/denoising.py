import os
import argparse
from pathlib import Path
from tqdm import tqdm
from alignment_utils import denoise  
def denoiser(src_path: Path, output_dir: str, extension: str = 'wav'):
    """
    Appliquer la réduction du bruit sur les fichiers audio dans le répertoire source.
    
    Args:
    - src_path (Path): Le répertoire contenant les fichiers audio à traiter.
    - output_dir (str): Répertoire où les fichiers audio débruités seront enregistrés.
    - extension (str): L'extension des fichiers audio à traiter (par défaut 'wav').
    """
    # Récupérer tous les fichiers audio du répertoire source avec l'extension spécifiée
    raw_src_audios = sorted(src_path.rglob(f'*.{extension}'))

    
    if not raw_src_audios:
        print(f"Aucun fichier audio avec l'extension .{extension} trouvé dans {src_path}.")
        return

    for src_audio in tqdm(raw_src_audios, desc='Traitement des fichiers audio'):
        # Extraire le nom du répertoire parent et le nom du fichier
        parent_dir = src_audio.parent.name
        file_name = src_audio.name

        # Construire le chemin de sortie
        out_audio_path = os.path.join(output_dir, parent_dir, file_name)
        
        # Créer les répertoires nécessaires pour la sortie
        os.makedirs(os.path.dirname(out_audio_path), exist_ok=True)

        # Appliquer la réduction du bruit
        denoise(src_audio, out_audio_path)

    print(f"Traitement terminé. Les fichiers ont été enregistrés dans {output_dir}")

def main():
    # Initialisation du parser d'arguments
    parser = argparse.ArgumentParser(description="Applique la réduction du bruit aux fichiers audio dans un répertoire.")
    
    parser.add_argument('--src_path', type=Path, required=True, help="Chemin du répertoire source contenant les fichiers audio.")
    parser.add_argument('--output_dir', type=str, required=True, help="Répertoire où les fichiers audio débruités seront enregistrés.")
    parser.add_argument('--extension', type=str, default='wav', help="L'extension des fichiers audio à traiter (par défaut 'wav').")

    # Récupérer les arguments
    args = parser.parse_args()

    # Lancer la réduction du bruit
    denoiser(args.src_path, args.output_dir, args.extension)

if __name__ == "__main__":
    main()

# usage
# python3 denoising.py --src_path "$src_path" --output_dir "$output_dir" --extension wav