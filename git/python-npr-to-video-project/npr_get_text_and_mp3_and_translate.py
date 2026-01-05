#!/usr/bin/env python3
"""
NPR Article Scraper with Translation - Lấy transcript, audio và dịch sang tiếng Việt
Tác giả: Script tự động
Ngày tạo: 2026-01-05
"""

import os
import sys
from pathlib import Path

# Import từ các module khác
from npr_get_text_and_mp3 import process_npr_article, get_user_input
from text_to_vietnamese import translate_text, save_vietnamese_text


def save_transcript_vietnamese(title, transcript_en, transcript_vi, folder_path):
    """Lưu transcript tiếng Việt với title"""
    print("\n💾 Đang lưu transcript tiếng Việt...")
    
    txt_file = folder_path / "transcript_vietnamese.txt"
    
    with open(txt_file, 'w', encoding='utf-8') as f:
        f.write(f"TITLE: {title}\n")
        f.write("=" * 70 + "\n")
        f.write(transcript_vi)
    
    print(f"✅ Đã lưu transcript tiếng Việt: {txt_file}")
    return txt_file


def main():
    """Main function"""
    try:
        # Lấy input
        url = get_user_input()
        
        # Xử lý bài viết NPR (lấy transcript và audio)
        folder_path, title, transcript_en, audio_file = process_npr_article(url)
        
        # Dịch transcript sang tiếng Việt
        transcript_vi = translate_text(transcript_en)
        
        # Lưu transcript tiếng Việt
        save_transcript_vietnamese(title, transcript_en, transcript_vi, folder_path)
        
        print("\n" + "=" * 70)
        print("✅ HOÀN THÀNH!")
        print(f"📁 Tất cả file đã được lưu vào: {folder_path}")
        print("   - transcript.txt (tiếng Anh)")
        print("   - transcript_vietnamese.txt (tiếng Việt)")
        if audio_file:
            print("   - audio.mp3")
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