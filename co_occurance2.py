import re
import pandas as pd
import numpy as np
from pathlib import Path
from collections import Counter
from tqdm import tqdm
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory

# ====================== KONFIGURASI SESUAI FLOWCHART ======================
# Dasar: Menggunakan hasil Weak Supervision
INPUT_FILE = Path("data/processed/weak_supervision/weak_supervision_results_v3.csv")
SEED_SPAREPART = Path("seed-list.csv")
SEED_GEJALA = Path("seed_gejala.csv")
SEED_ACTION = Path("seed_action.csv")

WINDOW_SIZE = 10  # Ukuran sliding window (bisa diubah untuk testing)
MIN_FREQ = 5      # Batas kemunculan minimal
# ===========================================================================

factory = StopWordRemoverFactory()
stopword_remover = factory.create_stop_word_remover()

extra_stopwords = {
    'mas', 'ini', 'kalau', 'ada', 'jadi', 'yang', 'apa', 'saya', 'sama', 
    'tidak', 'itu', 'sudah', 'juga', 'adalah', 'nya', 'ataupun', 'sekali', 
    'atas', 'wilayah', 'bagian', 'satu', 'kemudian', 'rumah', 'oke', 'nah',
    'dan', 'dengan', 'untuk', 'dari', 'dalam',"teman","hai","temen","mas","nah"
}

def load_all_seeds():
    """Memuat semua seed untuk jangkar dan evaluasi ground truth"""
    # Load Sparepart sebagai jangkar pencarian
    df_sp = pd.read_csv(SEED_SPAREPART)
    spareparts = set(df_sp['nama_sparepart'].str.lower().str.strip())
    
    # Load Gejala & Action untuk Ground Truth (Evaluasi Validasi)
    gejala = set()
    action = set()
    if SEED_GEJALA.exists():
        gejala = set(pd.read_csv(SEED_GEJALA).iloc[:, 0].str.lower().str.strip())
    if SEED_ACTION.exists():
        action = set(pd.read_csv(SEED_ACTION).iloc[:, 0].str.lower().str.strip())
        
    print(f"✅ Berhasil memuat: {len(spareparts)} Sparepart, {len(gejala)} Gejala, {len(action)} Action")
    return spareparts, gejala, action

def calculate_metrics(found_words, ground_truth):
    """Menghitung Precision, Recall, dan F1-Score"""
    found_words_set = set(found_words)
    
    # TP: Ada di temuan program & ada di kamus seed lama
    tp_list = found_words_set.intersection(ground_truth)
    tp = len(tp_list)
    
    # FP: Ada di temuan program tapi tidak ada di kamus (kandidat baru/noise)
    fp = len(found_words_set - ground_truth)
    
    # FN: Ada di kamus tapi gagal ditemukan program dalam window
    fn = len(ground_truth - found_words_set)
    
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    return {'precision': precision, 'recall': recall, 'f1': f1, 'tp': tp, 'fp': fp, 'fn': fn}

def extract_co_occurrences():
    spareparts, gejalas, actions = load_all_seeds()
    ground_truth = gejalas | actions
    
    if not INPUT_FILE.exists():
        print(f"❌ Error: File {INPUT_FILE} tidak ditemukan! Jalankan weak_supervision.py dulu.")
        return

    print(f"📖 Memproses dasar data: {INPUT_FILE.name}")
    df_ws = pd.read_csv(INPUT_FILE)
    
    co_occur = Counter()
    context_counter = Counter()
    
    # Proses baris demi baris dari hasil Weak Supervision
    for _, row in tqdm(df_ws.iterrows(), total=len(df_ws), desc="Analisis Co-occurrence"):
        sentence = str(row['sentence']).lower()
        words = re.findall(r'\b\w+\b', sentence)
        
        # Cari posisi sparepart dalam kalimat
        for i, word in enumerate(words):
            if word in spareparts:
                # Tentukan sliding window di sekitar sparepart
                start = max(0, i - WINDOW_SIZE)
                end = min(len(words), i + WINDOW_SIZE + 1)
                context = words[start:end]
                
                for ctx_word in context:
                    if ctx_word != word and len(ctx_word) > 2:
                        if ctx_word in extra_stopwords:
                            continue
                        
                        # Bersihkan dengan Sastrawi
                        cleaned = stopword_remover.remove(ctx_word)
                        if cleaned and len(cleaned) > 2:
                            co_occur[(word, cleaned)] += 1
                            context_counter[cleaned] += 1
    
    # Buat DataFrame hasil
    results = []
    for (sp, ctx), freq in co_occur.most_common():
        if freq >= MIN_FREQ:
            results.append({
                'sparepart': sp,
                'context_word': ctx,
                'frequency': freq
            })
    
    df_result = pd.DataFrame(results)
    
    # Simpan hasil untuk analisis bootstrapping
    output_dir = Path("data/analysis")
    output_dir.mkdir(parents=True, exist_ok=True)
    df_result.to_csv(output_dir / "co_occurrence_results.csv", index=False)
    
    # --- TAHAP EVALUASI VALIDASI ---
    found_unique = df_result['context_word'].unique()
    metrics = calculate_metrics(found_unique, ground_truth)
    
    print("\n" + "="*45)
    print(f"📊 VALIDASI SLIDING WINDOW (Size: {WINDOW_SIZE})")
    print("="*45)
    print(f"Precision : {metrics['precision']:.4f} (Ketepatan temuan)")
    print(f"Recall    : {metrics['recall']:.4f} (Cakupan terhadap Seed)")
    print(f"F1-Score  : {metrics['f1']:.4f}")
    print("-" * 45)
    print(f"TP (Sesuai Seed)    : {metrics['tp']}")
    print(f"FP (Kandidat/Noise) : {metrics['fp']}")
    print(f"FN (Terlewat)       : {metrics['fn']}")
    print("="*45)
    
    print("\n💡 Top 10 Kandidat Seed Baru (Discovery):")
    # Ambil yang masuk FP (tidak ada di seed lama) tapi frekuensi tinggi
    top_new = df_result[~df_result['context_word'].isin(ground_truth)]
    print(top_new.groupby('context_word')['frequency'].sum().nlargest(10))

if __name__ == "__main__":
    extract_co_occurrences()