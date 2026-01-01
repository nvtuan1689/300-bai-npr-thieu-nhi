#!/usr/bin/env python3
"""
NPR to MP4 Pipeline - Từ URL NPR đến video MP4 hoàn chỉnh
Tác giả: Script tự động
Ngày tạo: 2026-01-02

Pipeline:
1. Nhập URL NPR
2. Tải transcript và audio từ NPR (gọi npr_get_text_and_mp3.py)
3. Tạo video với phụ đề song ngữ (gọi mp3_and_text_to_mp4.py)
"""

import os
import sys
import subprocess
from pathlib import Path


def run_npr_scraper():
    """Chạy script tải transcript và audio từ NPR"""
    print("=" * 70)
    print("BƯỚC 1: TẢI TRANSCRIPT VÀ AUDIO TỪ NPR")
    print("=" * 70)
    
    # Chạy script npr_get_text_and_mp3.py
    result = subprocess.run(
        [sys.executable, "npr_get_text_and_mp3.py"],
        capture_output=False,
        text=True
    )
    
    if result.returncode != 0:
        print("❌ Lỗi khi tải từ NPR!")
        sys.exit(1)
    
    return result.returncode == 0


def find_latest_folder():
    """Tìm folder output mới nhất"""
    folders = [f for f in Path('.').iterdir() if f.is_dir() and f.name.count('_') >= 4]
    
    if not folders:
        print("❌ Không tìm thấy folder output từ NPR scraper!")
        sys.exit(1)
    
    # Sort theo thời gian tạo
    latest_folder = max(folders, key=lambda f: f.stat().st_mtime)
    return latest_folder


def find_audio_and_transcript(folder):
    """Tìm file audio và transcript trong folder"""
    audio_file = folder / "audio.mp3"
    transcript_file = folder / "transcript.txt"
    
    if not audio_file.exists():
        print(f"❌ Không tìm thấy audio.mp3 trong {folder}")
        sys.exit(1)
    
    if not transcript_file.exists():
        print(f"❌ Không tìm thấy transcript.txt trong {folder}")
        sys.exit(1)
    
    return str(audio_file), str(transcript_file)


def run_video_creator(mp3_path, txt_path):
    """Chạy script tạo video"""
    print("\n" + "=" * 70)
    print("BƯỚC 2: TẠO VIDEO VỚI PHỤ ĐỀ SONG NGỮ")
    print("=" * 70)
    
    # Import các hàm từ mp3_and_text_to_mp4
    from text_to_vietnamese import translate_text, save_vietnamese_text, read_transcript
    from mp3_and_text_and_translate_to_mp4 import create_video
    
    # Đọc transcript
    text_en = read_transcript(txt_path)
    
    # Dịch sang tiếng Việt
    text_vi = translate_text(text_en)
    
    # Lưu bản dịch
    vi_path = save_vietnamese_text(text_vi, txt_path)
    
    # Lấy output folder (cùng folder với mp3)
    output_folder = Path(mp3_path).parent
    
    # Tạo video
    video_path = create_video(mp3_path, text_en, text_vi, output_folder)
    
    return video_path, vi_path


def main():
    """Main function"""
    try:
        print("=" * 70)
        print("NPR TO MP4 PIPELINE - Từ URL NPR đến Video hoàn chỉnh")
        print("=" * 70)
        print()
        
        # Bước 1: Tải transcript và audio từ NPR
        print("🔹 Bước 1: Tải transcript và audio từ NPR")
        success = run_npr_scraper()
        
        if not success:
            print("❌ Không thể tải từ NPR!")
            sys.exit(1)
        
        # Tìm folder output mới nhất
        print("\n🔍 Đang tìm folder output mới nhất...")
        latest_folder = find_latest_folder()
        print(f"✅ Tìm thấy: {latest_folder}")
        
        # Tìm audio và transcript
        print("🔍 Đang tìm file audio và transcript...")
        mp3_path, txt_path = find_audio_and_transcript(latest_folder)
        print(f"✅ MP3: {mp3_path}")
        print(f"✅ TXT: {txt_path}")
        
        # Bước 2: Tạo video
        print("\n🔹 Bước 2: Tạo video với phụ đề song ngữ")
        video_path, vi_path = run_video_creator(mp3_path, txt_path)
        
        # Hoàn thành
        print("\n" + "=" * 70)
        print("🎉 HOÀN THÀNH PIPELINE!")
        print("=" * 70)
        print(f"📁 Folder output: {latest_folder}")
        print(f"📄 Transcript (EN): {txt_path}")
        print(f"📄 Transcript (VI): {vi_path}")
        print(f"🎵 Audio: {mp3_path}")
        print(f"🎬 Video: {video_path}")
        print("=" * 70)
    
    except KeyboardInterrupt:
        print("\n\n❌ Đã hủy bởi người dùng")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
