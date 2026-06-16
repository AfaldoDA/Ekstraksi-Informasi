# triplet_extraction_v2.py
import pandas as pd
from pathlib import Path
import sys

# ====================== KONFIGURASI PATH ======================
ROOT_DIR = Path(__file__).parent
INPUT_FILE = ROOT_DIR / "data" / "processed" / "extraction" / "hw_results.csv"
OUTPUT_DIR = ROOT_DIR / "data" / "processed" / "final_extraction"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
# ==============================================================

def generate_triplets():
    if not INPUT_FILE.exists():
        print(f"❌ File tidak ditemukan: {INPUT_FILE}")
        return

    # 1. Baca data dari IE2 (dengan safety net jika CSV kosong)
    try:
        df = pd.read_csv(INPUT_FILE)
    except pd.errors.EmptyDataError:
        df = pd.DataFrame()

    output_path = OUTPUT_DIR / "final_triplets_with_counts.csv"

    if df.empty or 'sparepart' not in df.columns:
        print("ℹ️ Data ekstraksi kosong. Membuat file triplet kosong.")
        pd.DataFrame(columns=['subject', 'relation', 'object', 'count']).to_csv(output_path, index=False)
        return

    triplets = []

    # 2. Proses pembentukan triplet
    for _, row in df.iterrows():
        sparepart = row['sparepart']
        
        # Gejala
        if pd.notna(row.get('gejala_terdeteksi')) and row['gejala_terdeteksi'] != "-":
            gejalas = str(row['gejala_terdeteksi']).split(', ')
            for g in gejalas:
                triplets.append({'subject': sparepart, 'relation': 'mengalami_gejala', 'object': g})

        # Action
        if pd.notna(row.get('action_terdeteksi')) and row['action_terdeteksi'] != "-":
            actions = str(row['action_terdeteksi']).split(', ')
            for a in actions:
                triplets.append({'subject': sparepart, 'relation': 'dilakukan_tindakan', 'object': a})

    # 3. Hitung dan simpan
    df_triplet = pd.DataFrame(triplets)
    
    if df_triplet.empty:
        print("ℹ️ Tidak ada triplet yang terbentuk. Membuat file triplet kosong.")
        pd.DataFrame(columns=['subject', 'relation', 'object', 'count']).to_csv(output_path, index=False)
    else:
        df_counts = df_triplet.groupby(['subject', 'relation', 'object']).size().reset_index(name='count')
        df_counts = df_counts.sort_values(by='count', ascending=False)
        df_counts.to_csv(output_path, index=False)
        
        print(f"Total kemunculan relasi: {df_counts['count'].sum()}")
        print(df_counts.head(20))
        print(f"File tersimpan di: {output_path}")

if __name__ == "__main__":
    generate_triplets()