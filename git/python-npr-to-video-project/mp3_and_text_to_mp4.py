#!/usr/bin/env python3
"""
MP3 và Text to MP4 Converter - Tạo video từ audio và transcript song ngữ
Tác giả: Script tự động
Ngày tạo: 2026-01-02
"""

import os
import sys
import json
import re
from pathlib import Path

# Import modules
from text_to_vietnamese import translate_text, save_vietnamese_text, read_transcript
from mp3_and_text_and_translate_to_mp4 import create_video


# Lưu input history vào trong file này dưới dạng comment
# HISTORY_START
LAST_INPUTS = {
    "mp3_path": "",
    "txt_path": ""
}
# HISTORY_END


def get_last_input(key):
    """Lấy input lần trước từ LAST_INPUTS"""
    return LAST_INPUTS.get(key, "")


def save_last_input(key, value):
    """Lưu input vào file script"""
    global LAST_INPUTS
    LAST_INPUTS[key] = value
    
    # Đọc nội dung file hiện tại
    with open(__file__, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Tìm và thay thế phần LAST_INPUTS
    pattern = r'(# HISTORY_START\nLAST_INPUTS = )({[^}]*})(# HISTORY_END)'
    new_dict = json.dumps(LAST_INPUTS, ensure_ascii=False, indent=4)
    replacement = f'\\1{new_dict}\n\\3'
    
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    # Ghi lại file
    with open(__file__, 'w', encoding='utf-8') as f:
        f.write(new_content)


def get_user_input():
    """Lấy input từ user"""
    print("=" * 70)
    print("MP3 & TEXT TO MP4 CONVERTER - Tạo video song ngữ")
    print("=" * 70)
    print()
    
    # Lấy MP3 path
    last_mp3 = get_last_input("mp3_path")
    if last_mp3:
        print(f"MP3 path lần trước: {last_mp3}")
    
    mp3_path = input("Nhập path đến file MP3 (hoặc Enter để dùng path lần trước): ").strip()
    
    if not mp3_path and last_mp3:
        mp3_path = last_mp3
        print(f"Sử dụng MP3: {mp3_path}")
    elif not mp3_path:
        print("❌ MP3 path không được để trống!")
        sys.exit(1)
    
    # Validate MP3
    if not os.path.exists(mp3_path):
        print(f"❌ File MP3 không tồn tại: {mp3_path}")
        sys.exit(1)
    
    # Lấy TXT path
    last_txt = get_last_input("txt_path")
    if last_txt:
        print(f"TXT path lần trước: {last_txt}")
    
    txt_path = input("Nhập path đến file TXT (hoặc Enter để dùng path lần trước): ").strip()
    
    if not txt_path and last_txt:
        txt_path = last_txt
        print(f"Sử dụng TXT: {txt_path}")
    elif not txt_path:
        print("❌ TXT path không được để trống!")
        sys.exit(1)
    
    # Validate TXT
    if not os.path.exists(txt_path):
        print(f"❌ File TXT không tồn tại: {txt_path}")
        sys.exit(1)
    
    # Lưu input
    save_last_input("mp3_path", mp3_path)
    save_last_input("txt_path", txt_path)
    
    return mp3_path, txt_path


def main():
    """Main function"""
    try:
        # Lấy input
        mp3_path, txt_path = get_user_input()
        
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
        
        print("\n" + "=" * 70)
        print("✅ HOÀN THÀNH!")
        print(f"📁 Video đã được lưu: {video_path}")
        print(f"📁 Bản dịch tiếng Việt: {vi_path}")
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
