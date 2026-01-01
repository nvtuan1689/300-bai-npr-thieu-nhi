#!/usr/bin/env python3
"""
MP3 and Text to MP4 Video Generator - Tạo video từ audio và transcript song ngữ
Tác giả: Script tự động
Ngày tạo: 2026-01-02
"""

from pathlib import Path
from moviepy.editor import *
from PIL import Image, ImageDraw, ImageFont
import numpy as np


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


def create_video(mp3_path, text_en, text_vi, output_folder, show_progress=True):
    """Tạo video MP4 từ audio và text"""
    if show_progress:
        print("\n🎬 Đang tạo video...")
    
    # Load audio
    audio_clip = AudioFileClip(mp3_path)
    duration = audio_clip.duration
    
    if show_progress:
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
    
    if show_progress:
        print(f"  Số chunks: {max_chunks}")
    
    # Thời gian cho mỗi chunk
    time_per_chunk = duration / max_chunks
    
    # Tạo video clips
    video_clips = []
    
    for i, (chunk_en, chunk_vi) in enumerate(zip(chunks_en, chunks_vi)):
        if show_progress:
            print(f"\r  Đang tạo frame {i+1}/{max_chunks}...", end='')
        
        # Tạo frame với highlight
        frame = create_text_frame(chunk_en, chunk_vi, highlight_en=True, highlight_vi=True)
        
        # Tạo clip từ frame
        clip = ImageClip(frame).set_duration(time_per_chunk)
        video_clips.append(clip)
    
    if show_progress:
        print()
    
    # Ghép các clips
    if show_progress:
        print("  Đang ghép video...")
    video = concatenate_videoclips(video_clips, method="compose")
    
    # Thêm audio
    video = video.set_audio(audio_clip)
    
    # Output path
    output_path = Path(output_folder) / "output_video.mp4"
    
    # Render video
    if show_progress:
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
    
    if show_progress:
        print(f"✅ Đã tạo video: {output_path}")
    
    return output_path


def main():
    """Main function - standalone usage"""
    import sys
    
    if len(sys.argv) < 4:
        print("Usage: python mp3_and_text_and_translate_to_mp4.py <mp3_path> <text_en> <text_vi> [output_folder]")
        sys.exit(1)
    
    mp3_path = sys.argv[1]
    text_en_path = sys.argv[2]
    text_vi_path = sys.argv[3]
    output_folder = sys.argv[4] if len(sys.argv) > 4 else Path(mp3_path).parent
    
    # Đọc text
    with open(text_en_path, 'r', encoding='utf-8') as f:
        text_en = f.read()
    
    with open(text_vi_path, 'r', encoding='utf-8') as f:
        text_vi = f.read()
    
    # Tạo video
    video_path = create_video(mp3_path, text_en, text_vi, output_folder)
    
    print(f"\n✅ Hoàn thành! Video: {video_path}")


if __name__ == "__main__":
    main()
