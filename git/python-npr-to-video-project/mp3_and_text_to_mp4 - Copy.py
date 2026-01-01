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
from datetime import datetime
from moviepy.editor import *
from moviepy.video.fx.all import *
from PIL import Image, ImageDraw, ImageFont
import numpy as np


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


def read_transcript(txt_path):
    """Đọc transcript từ file"""
    print(f"\n📖 Đang đọc transcript từ: {txt_path}")
    
    with open(txt_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Loại bỏ phần TITLE nếu có
    if content.startswith("TITLE:"):
        lines = content.split('\n')
        # Tìm dòng có "===" để bỏ qua header
        content_start = 0
        for i, line in enumerate(lines):
            if '===' in line:
                content_start = i + 1
                break
        content = '\n'.join(lines[content_start:]).strip()
    
    print(f"✅ Đã đọc: {len(content)} ký tự")
    return content


def translate_text(text):
    """Dịch text sang tiếng Việt"""
    print("\n🌐 Đang dịch sang tiếng Việt...")
    
    try:
        from deep_translator import GoogleTranslator
        
        # Chia text thành các đoạn nhỏ (Google Translate có giới hạn)
        max_length = 4500
        paragraphs = text.split('\n\n')
        translated_paragraphs = []
        
        translator = GoogleTranslator(source='en', target='vi')
        
        current_chunk = ""
        for para in paragraphs:
            if len(current_chunk) + len(para) < max_length:
                current_chunk += para + '\n\n'
            else:
                if current_chunk:
                    print(f"  Đang dịch đoạn {len(translated_paragraphs) + 1}...")
                    translated = translator.translate(current_chunk.strip())
                    translated_paragraphs.append(translated)
                current_chunk = para + '\n\n'
        
        # Dịch đoạn cuối
        if current_chunk:
            print(f"  Đang dịch đoạn {len(translated_paragraphs) + 1}...")
            translated = translator.translate(current_chunk.strip())
            translated_paragraphs.append(translated)
        
        vietnamese_text = '\n\n'.join(translated_paragraphs)
        print(f"✅ Đã dịch: {len(vietnamese_text)} ký tự")
        
        return vietnamese_text
    
    except ImportError:
        print("⚠️ Thư viện deep-translator chưa được cài đặt!")
        print("  Cài đặt: pip install deep-translator")
        print("  Tạm thời sử dụng bản dịch mẫu...")
        return "[Bản dịch tiếng Việt sẽ xuất hiện ở đây]\n\n" + text
    except Exception as e:
        print(f"⚠️ Lỗi khi dịch: {e}")
        print("  Sử dụng text gốc...")
        return text


def save_vietnamese_text(vietnamese_text, txt_path):
    """Lưu bản dịch tiếng Việt"""
    output_path = txt_path.replace('.txt', '_vietnamese.txt')
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(vietnamese_text)
    
    print(f"✅ Đã lưu bản dịch: {output_path}")
    return output_path


def split_text_into_chunks(text, chunk_size=300):
    """Chia text thành các chunk nhỏ để hiển thị"""
    # Chia theo paragraph trước
    paragraphs = text.split('\n\n')
    chunks = []
    current_chunk = ""
    
    for para in paragraphs:
        if len(current_chunk) + len(para) < chunk_size:
            current_chunk += para + '\n\n'
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = para + '\n\n'
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks


def wrap_text(text, font, max_width, draw):
    """Wrap text để vừa trong chiều rộng cho trước"""
    lines = []
    words = text.split()
    current_line = []
    
    for word in words:
        # Thử thêm word vào dòng hiện tại
        test_line = ' '.join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=font)
        width = bbox[2] - bbox[0]
        
        if width <= max_width:
            current_line.append(word)
        else:
            # Dòng đã đầy, lưu lại và bắt đầu dòng mới
            if current_line:
                lines.append(' '.join(current_line))
                current_line = [word]
            else:
                # Word quá dài, bắt buộc phải xuống dòng
                lines.append(word)
    
    # Thêm dòng cuối cùng
    if current_line:
        lines.append(' '.join(current_line))
    
    return '\n'.join(lines)


def create_text_frame(text_en, text_vi, width=1920, height=1080, highlight_en=False, highlight_vi=False):
    """Tạo frame với text song ngữ"""
    # Tạo background đen
    img = Image.new('RGB', (width, height), color=(0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Fonts
    try:
        font_en = ImageFont.truetype("arial.ttf", 32)
        font_vi = ImageFont.truetype("arial.ttf", 28)
        font_header = ImageFont.truetype("arial.ttf", 28)
    except:
        font_en = ImageFont.load_default()
        font_vi = ImageFont.load_default()
        font_header = ImageFont.load_default()
    
    # Vùng text
    left_x = 50
    right_x = width // 2 + 50
    y_start = 100
    max_width = width // 2 - 100
    
    # Background cho highlighted text
    if highlight_en:
        draw.rectangle([left_x - 10, y_start - 10, width // 2 - 50, height - 50], 
                      fill=(30, 30, 30), outline=(255, 255, 0), width=3)
    
    if highlight_vi:
        draw.rectangle([right_x - 10, y_start - 10, width - 50, height - 50], 
                      fill=(30, 30, 30), outline=(255, 255, 0), width=3)
    
    # Wrap text để vừa trong khung
    wrapped_text_en = wrap_text(text_en, font_en, max_width, draw)
    wrapped_text_vi = wrap_text(text_vi, font_vi, max_width, draw)
    
    # Vẽ text English (bên trái)
    color_en = (255, 255, 0) if highlight_en else (255, 255, 255)
    draw.multiline_text((left_x, y_start), wrapped_text_en, font=font_en, fill=color_en, spacing=5)
    
    # Vẽ text Vietnamese (bên phải)
    color_vi = (255, 255, 0) if highlight_vi else (200, 200, 255)
    draw.multiline_text((right_x, y_start), wrapped_text_vi, font=font_vi, fill=color_vi, spacing=5)
    
    # Header
    draw.text((left_x, 30), "English Transcript", font=font_header, fill=(150, 150, 150))
    draw.text((right_x, 30), "Bản dịch tiếng Việt", font=font_header, fill=(150, 150, 150))
    
    return np.array(img)


def create_video(mp3_path, text_en, text_vi, output_folder):
    """Tạo video MP4 từ audio và text"""
    print("\n🎬 Đang tạo video...")
    
    # Load audio
    audio_clip = AudioFileClip(mp3_path)
    duration = audio_clip.duration
    
    print(f"  Audio duration: {duration:.1f} seconds")
    
    # Chia text thành chunks
    chunks_en = split_text_into_chunks(text_en, chunk_size=400)
    chunks_vi = split_text_into_chunks(text_vi, chunk_size=400)
    
    # Đảm bảo 2 list có cùng độ dài
    max_chunks = max(len(chunks_en), len(chunks_vi))
    while len(chunks_en) < max_chunks:
        chunks_en.append("")
    while len(chunks_vi) < max_chunks:
        chunks_vi.append("")
    
    print(f"  Số chunks: {max_chunks}")
    
    # Thời gian cho mỗi chunk
    time_per_chunk = duration / max_chunks
    
    # Tạo video clips
    video_clips = []
    
    for i, (chunk_en, chunk_vi) in enumerate(zip(chunks_en, chunks_vi)):
        print(f"\r  Đang tạo frame {i+1}/{max_chunks}...", end='')
        
        # Tạo frame với highlight
        frame = create_text_frame(chunk_en, chunk_vi, highlight_en=True, highlight_vi=True)
        
        # Tạo clip từ frame
        clip = ImageClip(frame).set_duration(time_per_chunk)
        video_clips.append(clip)
    
    print()
    
    # Ghép các clips
    print("  Đang ghép video...")
    video = concatenate_videoclips(video_clips, method="compose")
    
    # Thêm audio
    video = video.set_audio(audio_clip)
    
    # Output path
    output_path = Path(output_folder) / "output_video.mp4"
    
    # Render video
    print(f"  Đang render video: {output_path}")
    video.write_videofile(
        str(output_path),
        fps=24,
        codec='libx264',
        audio_codec='aac',
        temp_audiofile='temp-audio.m4a',
        remove_temp=True,
        verbose=False,
        logger=None
    )
    
    # Cleanup
    audio_clip.close()
    video.close()
    
    print(f"✅ Đã tạo video: {output_path}")
    return output_path


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
