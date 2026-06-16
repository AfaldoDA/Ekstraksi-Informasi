import sys
from pathlib import Path
import yt_dlp
import re
import shutil

ROOT_DIR = Path(__file__).parent
sys.path.append(str(ROOT_DIR))

class ExtractionPipeline:
    def __init__(self):
        # Base folder smntara
        self.data_dir = ROOT_DIR / "data"

    def clean_vtt_text(self, vtt_path: Path) -> str:
        """Membersihkan file VTT dari yt-dlp menjadi teks mentah (raw text)"""
        with open(vtt_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        cleaned_lines = []
        for line in lines:
            if 'WEBVTT' in line or not line.strip() or '-->' in line:
                continue
            clean_line = re.sub(r'<[^>]+>', '', line).strip()
            if clean_line and (not cleaned_lines or clean_line != cleaned_lines[-1]):
                cleaned_lines.append(clean_line)
        return "\n".join(cleaned_lines)

    def download_video(self, youtube_url: str) -> bool:
        """Mengunduh subtitle 1 video menggunakan yt-dlp"""
        raw_dir = self.data_dir / "raw"
        
        # cleaner folder raw 
        if raw_dir.exists():
            shutil.rmtree(raw_dir)
        raw_dir.mkdir(parents=True, exist_ok=True)

        ydl_opts = {
            'skip_download': True,
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': ['id'],
            'subtitlesformat': 'vtt',
            'outtmpl': str(raw_dir / 'demo_video.%(ext)s'),
            'quiet': True,
            'no_warnings': True
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([youtube_url])
            vtt_files = list(raw_dir.glob("*.vtt"))
            
            if not vtt_files:
                return False
                
            raw_text = self.clean_vtt_text(vtt_files[0])
            with open(raw_dir / "demo_video.txt", "w", encoding="utf-8") as f:
                f.write(raw_text)
                
            vtt_files[0].unlink() # Hapus VTT
            return True
        except Exception as e:
            print(f"Error yt-dlp: {e}")
            return False

    def run_full_pipeline(self):
        """Memanggil semua script dari file copy-an TANPA argumen"""
        
        print("Mulai Preprocessing...")
        import preprocessing
        preprocessing.process_files()
        
        print("Mulai Weak Supervision...")
        import weak_supervision
        weak_supervision.main() 
        
        print("Mulai Hiding Window...")
        import IE2 
        IE2.run_extraction_with_validation()
        
        print("Mulai Triplet...")
        import triplet
        triplet.generate_triplets()