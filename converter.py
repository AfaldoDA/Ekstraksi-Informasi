import re
import pandas as pd
from pathlib import Path
from tqdm import tqdm

INPUT_FOLDER = Path("data-txt")
OUTPUT_FOLDER = Path("data/processed/cleaned")
OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

print(f"Input folder : {INPUT_FOLDER.absolute()}")
print(f"Output folder: {OUTPUT_FOLDER.absolute()}\n")


def clean_subtitle_text(text: str) -> str:
    if not text or not isinstance(text, str):
        return ""

    # Header VTT
    text = re.sub(r'WEBVTT.*?\n\n', '', text, flags=re.DOTALL | re.IGNORECASE)
    
    # Timestamp 
    text = re.sub(r'\d{2}:\d{2}:\d{2}[.,]\d{3}\s*-->\s*\d{2}:\d{2}:\d{2}[.,]\d{3}.*', '', text)
    text = re.sub(r'<\d{2}:\d{2}:\d{2}\.\d{3}>', '', text)
    
    # Tag dan noise
    text = re.sub(r'</?c>', '', text)
    text = re.sub(r'align:start position:\d+%', '', text)
    
    #[musik], [tertawa], dll
    text = re.sub(r'\s*\[.*?\]\s*', ' ', text)
    
    # Hapus nomor cue
    text = re.sub(r'^\s*\d+\s*$', '', text, flags=re.MULTILINE)
    
    # Bersihkan karakter aneh
    text = re.sub(r'[^\w\s.,!?\'"-–—:;()]', ' ', text)
    text = re.sub(r' +', ' ', text).strip()
    
    return text


def process_all_files():
    # Hanya .vtt dan .srt + recursive (termasuk subfolder)
    all_files = []
    all_files.extend(INPUT_FOLDER.glob("**/*.vtt"))
    all_files.extend(INPUT_FOLDER.glob("**/*.srt"))
    
    print(f"Total file .vtt + .srt ditemukan: {len(all_files)}\n")
    
    if not all_files:
        print("Tidak ada file .vtt atau .srt ditemukan!")
        return
    
    results = []
    
    for file_path in tqdm(all_files, desc="Cleaning"):
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                raw_text = f.read()
            
            cleaned_text = clean_subtitle_text(raw_text)
            
            # Nama file output yang bersih
            clean_name = re.sub(r'[^\w\s-]', '', file_path.stem)
            clean_name = re.sub(r'\s+', '_', clean_name.strip())[:120]
            output_path = OUTPUT_FOLDER / f"cleaned_{clean_name}.txt"
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(cleaned_text)
            
            results.append({
                'original': file_path.name,
                'output': output_path.name,
                'length': len(cleaned_text),
                'status': 'success'
            })
            
        except Exception as e:
            print(f"Error {file_path.name}: {e}")
    
    pd.DataFrame(results).to_csv(OUTPUT_FOLDER / "cleaning_report.csv", index=False)
    
    print(f"\n🎉 Cleaning selesai! Total file diproses: {len(results)}")
    print(f"Hasil disimpan di: {OUTPUT_FOLDER}")


if __name__ == "__main__":
    process_all_files()