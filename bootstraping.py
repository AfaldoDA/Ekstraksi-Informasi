import pandas as pd
from pathlib import Path
import re
from collections import Counter
from tqdm import tqdm


PREPROCESSED_DIR = Path("data/processed/preprocessed")
SEED_LIST_FILE = Path("seed-list.csv")
GEJALA_FILE = Path("seed_gejala.csv")
ACTION_FILE = Path("seed_action.csv")
OUTPUT_DIR = Path("data/processed/bootstrapping")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

WINDOW_SIZE = 5

def load_existing_seeds():
    spareparts = set(pd.read_csv(SEED_LIST_FILE)['nama_sparepart'].str.lower())
    gejalas = set(pd.read_csv(GEJALA_FILE)['nama_gejala'].str.lower())
    actions = set(pd.read_csv(ACTION_FILE)['nama_action'].str.lower())
    return spareparts, gejalas, actions

def discover_new_candidates():
    spareparts, existing_gejalas, existing_actions = load_existing_seeds()
    all_existing_seeds = existing_gejalas | existing_actions
    
    candidate_words = Counter()
    prep_files = list(PREPROCESSED_DIR.glob("prep_*.txt"))
    
    print(f"🔍 Mencari kandidat seed baru di {len(prep_files)} file...")
    
    for file_path in tqdm(prep_files):
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.lower()
                for part in spareparts:
                    if part in line:
                        # Ambil window di sekitar sparepart
                        words = re.findall(r'\b\w+\b', line)
                        try:
                            idx = words.index(part.split()[0]) # Ambil kata pertama jika multi-word
                            start = max(0, idx - WINDOW_SIZE)
                            end = min(len(words), idx + WINDOW_SIZE + 1)
                            
                            context = words[start:end]
                            for word in context:
                                # Kriteria kandidat: bukan sparepart, bukan seed lama, panjang > 3
                                if (word not in spareparts and 
                                    word not in all_existing_seeds and 
                                    len(word) > 3):
                                    candidate_words[word] += 1
                        except ValueError:
                            continue

   
    df_candidates = pd.DataFrame(candidate_words.most_common(100), columns=['candidate_word', 'frequency'])
    
    output_path = OUTPUT_DIR / "candidate_seeds_v1.csv"
    df_candidates.to_csv(output_path, index=False)
    
    
    print(f"Dir: {output_path}")
    print(df_candidates.head(20))

if __name__ == "__main__":
    discover_new_candidates()