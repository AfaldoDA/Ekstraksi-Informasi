import re
from pathlib import Path
from tqdm import tqdm
import pandas as pd
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory

# ====================== KONFIGURASI PATH ======================
# Mengunci direktori relatif ke folder 'streamlit' ini
ROOT_DIR = Path(__file__).parent

INPUT_FOLDER = ROOT_DIR / "data" / "raw"
OUTPUT_FOLDER = ROOT_DIR / "data" / "processed" / "preprocessed"
OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)
# ==============================================================

factory = StopWordRemoverFactory()
stopword_remover = factory.create_stop_word_remover()

custom_fillers = {
    'sini', 'tadi', 'begini', 'gak', 'enggak', 'begitu', 'toh', 'iya', 'loh', 'nah',
    'oke', 'ok', 'ya', 'mas bro', 'masbro', 'bro', 'sayang', 'monggo', 'mong', 
    'perhatikan', 'penjeran', 'jan', 'no', 'noh', 'du', 'duk', 'ee', 'e', 'nih',
    'ayo', 'dengar', 'lihat', 'kan', 'dulu', 'baru', 'sekarang', 'mana',"teman","temen","mas","nah"
}

INTRO_PATTERNS = [
    'halo guys', 'selamat pagi', 'assalamualaikum', 'asalamualaikum',
    'warahmatullahi', 'wabarakatuh', 'jumpa lagi', 'dengan kami di'
]

def is_intro_sentence(sentence: str) -> bool:
    """Cek apakah kalimat termasuk intro/salam"""
    sent_lower = sentence.lower()
    return any(pattern in sent_lower for pattern in INTRO_PATTERNS)

def clean_sentence(sentence: str) -> str:
    if not sentence or len(sentence.strip()) < 15:
        return None
    
    sentence = sentence.lower().strip()
    
    # Hapus intro/salam
    if is_intro_sentence(sentence):
        return None
    
    # Hapus stopwords (Sastrawi)
    sentence = stopword_remover.remove(sentence)
    
    # Hapus custom fillers
    words = sentence.split()
    cleaned_words = [w for w in words if w not in custom_fillers]
    
    sentence = ' '.join(cleaned_words)
    sentence = re.sub(r' +', ' ', sentence).strip()
    
    # Filter akhir: minimal 20 karakter atau minimal 5 kata
    if len(sentence) < 20 or len(sentence.split()) < 5:
        return None
    
    return sentence.capitalize() + "."

def process_files():
    # Mengambil semua file txt (termasuk demo_video.txt dari yt-dlp)
    raw_files = list(INPUT_FOLDER.glob("*.txt"))
    print(f"Ditemukan {len(raw_files)} file untuk diproses...\n")
    
    if not raw_files:
        print(f"❌ Tidak ada file teks di {INPUT_FOLDER}")
        return

    total_sentences = 0
    all_cleaned_sentences = [] # Untuk disatukan ke dalam CSV
    
    for file_path in tqdm(raw_files, desc="Preprocessing"):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            # Pisahkan berdasarkan titik, tanda seru, tanya, atau baris baru
            raw_sentences = re.split(r'[.!?\n]+', text)
            cleaned_sentences = []
            
            for sent in raw_sentences:
                cleaned = clean_sentence(sent)
                if cleaned:
                    # Cek duplikasi agar tidak ada kalimat identik berulang
                    if not any(cleaned.lower() in existing.lower() for existing in cleaned_sentences):
                        cleaned_sentences.append(cleaned)
                        all_cleaned_sentences.append(cleaned)
            
            total_sentences += len(cleaned_sentences)
            
        except Exception as e:
            print(f"Error {file_path.name}: {e}")
    
    # Simpan hasil dalam format CSV yang dibutuhkan oleh weak_supervision.py
    if all_cleaned_sentences:
        df_output = pd.DataFrame({'sentence': all_cleaned_sentences})
        output_csv = OUTPUT_FOLDER / "preprocessed_sentences.csv"
        df_output.to_csv(output_csv, index=False)
        
        print("\n🎉 Preprocessing selesai!")
        print(f"Total kalimat bersih: {total_sentences:,}")
        print(f"File output siap dieksekusi: {output_csv}")
    else:
        print("\n⚠️ Preprocessing selesai, tetapi tidak ada kalimat yang lolos filter.")
        # Buat CSV kosong agar sistem tidak crash
        pd.DataFrame(columns=['sentence']).to_csv(OUTPUT_FOLDER / "preprocessed_sentences.csv", index=False)

if __name__ == "__main__":
    process_files()