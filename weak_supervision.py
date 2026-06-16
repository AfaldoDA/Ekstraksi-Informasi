import pandas as pd
from pathlib import Path
from tqdm import tqdm
import re

# ====================== KONFIGURASI PATH ======================
ROOT_DIR = Path(__file__).parent
PREPROCESSED_FILE = ROOT_DIR / "data" / "processed" / "preprocessed" / "preprocessed_sentences.csv"
SEED_DIR = ROOT_DIR
OUTPUT_DIR = ROOT_DIR / "data" / "processed" / "weak_supervision"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
# ==============================================================

def load_seeds():
    sparepart = set()
    gejala = set()
    action = set()
    
    # Load Sparepart
    for filename in ["seed_sparepart.csv", "seed-list.csv"]:
        if (SEED_DIR / filename).exists():
            df = pd.read_csv(SEED_DIR / filename)
            sparepart = set(str(x).lower().strip() for x in df.iloc[:, 0] if pd.notna(x))
            break
    
    # Load Gejala & Action
    if (SEED_DIR / "seed_gejala.csv").exists():
        df = pd.read_csv(SEED_DIR / "seed_gejala.csv")
        gejala = set(str(x).lower().strip() for x in df.iloc[:, 0] if pd.notna(x))
    
    if (SEED_DIR / "seed_action.csv").exists():
        df = pd.read_csv(SEED_DIR / "seed_action.csv")
        action = set(str(x).lower().strip() for x in df.iloc[:, 0] if pd.notna(x))
    
    print(f" Loaded - Sparepart: {len(sparepart)}, Gejala: {len(gejala)}, Action: {len(action)}")
    return sparepart, gejala, action


def main():
    spareparts, gejalas, actions = load_seeds()
    
    # 1. Cek apakah file preprocessed_sentences.csv ada
    if not PREPROCESSED_FILE.exists():
        print(f"❌ File {PREPROCESSED_FILE} tidak ditemukan!")
        return
        
    try:
        df_input = pd.read_csv(PREPROCESSED_FILE)
    except pd.errors.EmptyDataError:
        df_input = pd.DataFrame()
        
    results = []
    
    # 2. Proses Scoring dari DataFrame
    if not df_input.empty and 'sentence' in df_input.columns:
        sentences = df_input['sentence'].dropna().tolist()
        
        for i, sent in enumerate(tqdm(sentences, desc="Scoring kalimat")):
            if len(str(sent).strip()) < 25:
                continue
                
            sent_lower = str(sent).lower()
            
            # --- PATCH: Deteksi Entitas Multi-Kata Menggunakan Regex ---
            sparepart_found = {sp for sp in spareparts if re.search(rf'\b{re.escape(sp)}\b', sent_lower)}
            
            if not sparepart_found:
                continue
            
            # Cari gejala dan action utuh di dalam kalimat
            gejala_found = {g for g in gejalas if re.search(rf'\b{re.escape(g)}\b', sent_lower)}
            action_found = {a for a in actions if re.search(rf'\b{re.escape(a)}\b', sent_lower)}
            
            gejala_count = len(gejala_found)
            action_count = len(action_found)
            # ----------------------------------------------------------
            
            # Hitung skor
            score = len(sparepart_found) * 5 + gejala_count * 3 + action_count * 2
            
            # Bonus jika sparepart dan gejala/action muncul bersama
            if gejala_count > 0 or action_count > 0:
                score += 10
            
            if score >= 8:
                results.append({
                    'filename': 'demo_video', 
                    'sentence_id': i,
                    'sentence': sent,
                    'sparepart_count': len(sparepart_found),
                    'gejala_count': gejala_count,
                    'action_count': action_count,
                    'total_score': score,
                    'spareparts_found': ", ".join(sparepart_found)
                })
    
    # 3. Simpan Hasil
    df_result = pd.DataFrame(results)
    output_file = OUTPUT_DIR / "weak_supervision_results_v3.csv"
    
    if not df_result.empty:
        df_result = df_result.sort_values(by='total_score', ascending=False)
        df_result.to_csv(output_file, index=False)
        print(f"\n✅ Total kalimat relevan : {len(df_result)}")
        print(f"📁 Hasil disimpan: {output_file}")
    else:
        print("\n⚠️ Tidak ada kalimat yang mencapai skor minimal 8.")
        pd.DataFrame(columns=[
            'filename', 'sentence_id', 'sentence', 'sparepart_count', 
            'gejala_count', 'action_count', 'total_score', 'spareparts_found'
        ]).to_csv(output_file, index=False)

if __name__ == "__main__":
    main()