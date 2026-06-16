import pandas as pd
from pathlib import Path
import re
from tqdm import tqdm

# ====================== KONFIGURASI ======================
ROOT_DIR = Path(__file__).parent

WS_RESULTS_FILE = ROOT_DIR / "data" / "processed" / "weak_supervision" / "weak_supervision_results_v3.csv"
SEED_DIR = ROOT_DIR 
OUTPUT_DIR = ROOT_DIR / "data" / "processed" / "extraction"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

WINDOW_SIZE = 15  
# =========================================================

def load_triggers():
    gejala = set()
    action = set()
    
    file_gejala = SEED_DIR / "seed_gejala.csv"
    if file_gejala.exists():
        df = pd.read_csv(file_gejala)
        gejala = set(str(x).lower().strip() for x in df.iloc[:, 0] if pd.notna(x))
        
    file_action = SEED_DIR / "seed_action.csv"
    if file_action.exists():
        df = pd.read_csv(file_action)
        action = set(str(x).lower().strip() for x in df.iloc[:, 0] if pd.notna(x))
        
    return gejala, action

def extract_context_window(sentence, entity, window_size):
    """Logika Hiding Window yang mendukung Entitas Multi-Kata"""
    words = re.findall(r'\b\w+\b', sentence.lower())
    entity_words = re.findall(r'\b\w+\b', entity.lower())
    entity_len = len(entity_words)
    
    contexts = []
    if entity_len == 0:
        return contexts
        
    # Geser pembacaan sepanjang list kata
    for i in range(len(words) - entity_len + 1):
        # Cek apakah potongan list kata ini sama persis dengan entitas multi-kata
        if words[i:i+entity_len] == entity_words:
            start = max(0, i - window_size)
            end = min(len(words), i + entity_len + window_size)
            
            left_window = words[start:i]
            right_window = words[i+entity_len:end]
            contexts.append({'left': left_window, 'right': right_window})
            
    return contexts

def run_extraction_with_validation():
    gejalas, actions = load_triggers()
    
    if not WS_RESULTS_FILE.exists():
        print(f"❌ File {WS_RESULTS_FILE} tidak ditemukan!")
        return

    try:
        df_ws = pd.read_csv(WS_RESULTS_FILE)
    except pd.errors.EmptyDataError:
        df_ws = pd.DataFrame()

    output_file = OUTPUT_DIR / "hw_results.csv"

    if df_ws.empty or 'sentence' not in df_ws.columns or 'spareparts_found' not in df_ws.columns:
        print("ℹ️ Data Weak Supervision kosong (tidak ada entitas otomotif).")
        pd.DataFrame(columns=['sentence', 'sparepart', 'gejala_terdeteksi', 'action_terdeteksi']).to_csv(output_file, index=False)
        return

    extraction_results = []
    tp = 0
    fp = 0 
    
    print(f"⚙️ Menjalankan Ekstraksi (Window Size: {WINDOW_SIZE})...")
    
    for _, row in tqdm(df_ws.iterrows(), total=len(df_ws)):
        sentence = str(row['sentence'])
        if pd.isna(row['spareparts_found']):
            continue
            
        spareparts = str(row['spareparts_found']).split(', ')
        
        for part in spareparts:
            contexts = extract_context_window(sentence, part, WINDOW_SIZE)
            
            for ctx in contexts:
                # --- PATCH: Gabungkan kata di jendela menjadi string utuh ---
                context_str = " ".join(ctx['left'] + ctx['right'])
                
                # Deteksi multi-word menggunakan regex untuk gejala dan action
                found_gejala = [g for g in gejalas if re.search(rf'\b{re.escape(g)}\b', context_str)]
                found_action = [a for a in actions if re.search(rf'\b{re.escape(a)}\b', context_str)]
                # ------------------------------------------------------------
                
                if found_gejala or found_action:
                    extraction_results.append({
                        'sentence': sentence,
                        'sparepart': part,
                        'gejala_terdeteksi': ", ".join(found_gejala) if found_gejala else "-",
                        'action_terdeteksi': ", ".join(found_action) if found_action else "-"
                    })
                    tp += len(found_gejala) + len(found_action)
                else:
                    fp += 1 

    df_result = pd.DataFrame(extraction_results)
    
    if df_result.empty:
        df_result = pd.DataFrame(columns=['sentence', 'sparepart', 'gejala_terdeteksi', 'action_terdeteksi'])
        
    df_result.to_csv(output_file, index=False)
    
    total_expected = len(df_ws) 
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = len(df_result) / total_expected if total_expected > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

    print("\n" + "="*40)
    print(f"📊 VALIDASI HIDING WINDOW (WS: {WINDOW_SIZE})")
    print("="*40)
    print(f"Total Kalimat Input   : {total_expected}")
    print(f"Total Relasi Diekstrak: {len(df_result)}")
    print("-" * 40)
    print(f"Precision : {precision:.4f}")
    print(f"Recall    : {recall:.4f}")
    print(f"F1-Score  : {f1:.4f}")
    print("="*40)
    print(f"✅ Hasil disimpan ke: {output_file}")

if __name__ == "__main__":
    run_extraction_with_validation()