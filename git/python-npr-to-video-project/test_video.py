#!/usr/bin/env python3
"""
Test script cho mp3_and_text_to_mp4.py
"""

import os
from pathlib import Path

# Tìm file mp3 và txt gần nhất
base_dir = Path(__file__).parent

# Tìm các folder có format YYYY_MM_DD__HH_MM
folders = sorted([f for f in base_dir.iterdir() if f.is_dir() and f.name.startswith('202')], reverse=True)

if folders:
    latest_folder = folders[0]
    print(f"✅ Tìm thấy folder mới nhất: {latest_folder}")
    
    # Tìm mp3 và txt
    mp3_file = latest_folder / "audio.mp3"
    txt_file = latest_folder / "transcript.txt"
    
    if mp3_file.exists() and txt_file.exists():
        print(f"✅ MP3: {mp3_file}")
        print(f"✅ TXT: {txt_file}")
        print()
        print("Bạn có thể chạy:")
        print(f'python mp3_and_text_to_mp4.py')
        print()
        print(f"Và nhập:")
        print(f"  MP3 path: {mp3_file}")
        print(f"  TXT path: {txt_file}")
    else:
        print("❌ Không tìm thấy audio.mp3 hoặc transcript.txt")
else:
    print("❌ Không tìm thấy folder nào")
