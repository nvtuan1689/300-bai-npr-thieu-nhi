#!/usr/bin/env python3
"""
MP3 and Text to MP4 Video Generator - Tạo video từ audio và transcript song ngữ
Tác giả: Script tự động
Ngày tạo: 2026-01-02
"""

import json
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


def create_scrolling_text_frame(full_text_en, full_text_vi, highlight_start, highlight_end, 
                                width=1920, height=1080, font_size_en=32, font_size_vi=28):
    """
    Tạo frame với toàn bộ text và highlight phần đang đọc
    
    Args:
        full_text_en: Toàn bộ text tiếng Anh
        full_text_vi: Toàn bộ text tiếng Việt
        highlight_start: Vị trí bắt đầu highlight (index)
        highlight_end: Vị trí kết thúc highlight (index)
    """
    # Tạo background đen
    img = Image.new('RGB', (width, height), color=(0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Fonts
    try:
        font_en = ImageFont.truetype("arial.ttf", font_size_en)
        font_vi = ImageFont.truetype("arial.ttf", font_size_vi)
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
    line_spacing = 10
    
    # Wrap toàn bộ text
    wrapped_en = wrap_text(full_text_en, font_en, max_width, draw)
    wrapped_vi = wrap_text(full_text_vi, font_vi, max_width, draw)
    
    # Tính toán vị trí của highlight trong wrapped text
    # Chia thành các dòng
    lines_en = wrapped_en.split('\n')
    lines_vi = wrapped_vi.split('\n')
    
    # Tìm dòng chứa highlight (dựa vào số ký tự)
    char_count = 0
    highlight_line_start = 0
    highlight_line_end = len(lines_en) - 1
    
    for i, line in enumerate(lines_en):
        line_char_count = len(line)
        if char_count <= highlight_start < char_count + line_char_count:
            highlight_line_start = i
        if char_count <= highlight_end < char_count + line_char_count:
            highlight_line_end = i
            break
        char_count += line_char_count + 1  # +1 for newline
    
    # Tính scroll offset để giữ highlight ở giữa màn hình
    available_height = height - y_start - 100
    line_height = font_size_en + line_spacing
    visible_lines = int(available_height / line_height)
    
    # Scroll để highlight_line ở giữa màn hình (hoặc gần đầu nếu chưa đủ text)
    target_line = highlight_line_start
    scroll_offset = max(0, target_line - visible_lines // 3)  # Giữ highlight ở 1/3 màn hình
    
    # Vẽ text English (bên trái)
    y_pos = y_start
    for i, line in enumerate(lines_en):
        if i < scroll_offset:
            continue  # Skip lines above visible area
        
        line_y = y_pos + (i - scroll_offset) * line_height
        if line_y > height - 100:
            break  # Stop if below visible area
        
        # Check if this line should be highlighted
        if highlight_line_start <= i <= highlight_line_end:
            # Highlight line
            color = (255, 50, 50)  # Đỏ
            # Draw background for highlight
            bbox = draw.textbbox((left_x, line_y), line, font=font_en)
            draw.rectangle([bbox[0]-5, bbox[1]-3, bbox[2]+5, bbox[3]+3], 
                          fill=(50, 20, 20), outline=(255, 50, 50), width=2)
        else:
            color = (200, 200, 200)  # Xám nhạt
        
        draw.text((left_x, line_y), line, font=font_en, fill=color)
    
    # Vẽ text Vietnamese (bên phải) - sync scroll với English
    y_pos = y_start
    for i, line in enumerate(lines_vi):
        if i < scroll_offset:
            continue
        
        line_y = y_pos + (i - scroll_offset) * line_height
        if line_y > height - 100:
            break
        
        # Highlight cùng dòng với English
        if highlight_line_start <= i <= highlight_line_end:
            color = (255, 100, 100)  # Đỏ nhạt hơn
            bbox = draw.textbbox((right_x, line_y), line, font=font_vi)
            draw.rectangle([bbox[0]-5, bbox[1]-3, bbox[2]+5, bbox[3]+3], 
                          fill=(50, 20, 20), outline=(255, 100, 100), width=2)
        else:
            color = (180, 180, 200)  # Xanh xám nhạt
        
        draw.text((right_x, line_y), line, font=font_vi, fill=color)
    
    # Header
    draw.rectangle([0, 0, width, 80], fill=(20, 20, 20))
    draw.text((left_x, 30), "English Transcript", font=font_header, fill=(150, 150, 150))
    draw.text((right_x, 30), "Bản dịch tiếng Việt", font=font_header, fill=(150, 150, 150))
    
    return np.array(img)


def load_timestamps(timestamps_path):
    """Load timestamps từ file JSON (nếu có)"""
    if Path(timestamps_path).exists():
        with open(timestamps_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None


def create_video_with_timestamps(mp3_path, text_en, text_vi, timestamps, output_folder, show_progress=True):
    """Tạo video MP4 với timestamps chính xác từ Whisper - Karaoke style"""
    if show_progress:
        print("\n🎬 Đang tạo video với timestamps (karaoke style)...")
    
    # Load audio
    audio_clip = AudioFileClip(mp3_path)
    duration = audio_clip.duration
    
    if show_progress:
        print(f"  Audio duration: {duration:.1f} seconds")
        print(f"  Số segments: {len(timestamps)}")
    
    # Dịch toàn bộ text một lần
    from text_to_vietnamese import translate_text
    if show_progress:
        print("  Đang dịch toàn bộ text...")
    text_vi_full = translate_text(text_en, show_progress=False)
    
    # Tạo mapping từ timestamps sang character positions
    char_positions = []
    current_pos = 0
    
    for seg in timestamps:
        seg_text = seg['text'].strip()
        # Tìm vị trí của segment trong full text
        pos = text_en.find(seg_text, current_pos)
        if pos == -1:
            pos = current_pos  # Fallback
        
        char_positions.append({
            'start_time': seg['start'],
            'end_time': seg['end'],
            'char_start': pos,
            'char_end': pos + len(seg_text)
        })
        current_pos = pos + len(seg_text)
    
    if show_progress:
        print(f"  Đang tạo {len(char_positions)} frames với karaoke effect...")
    
    # Tạo video clips - mỗi segment một frame
    video_clips = []
    
    for i, pos_info in enumerate(char_positions):
        if show_progress:
            print(f"\r  Frame {i+1}/{len(char_positions)}...", end='')
        
        # Tạo frame với full text và highlight segment hiện tại
        frame = create_scrolling_text_frame(
            text_en, 
            text_vi_full,
            pos_info['char_start'],
            pos_info['char_end']
        )
        
        # Duration = end - start
        seg_duration = pos_info['end_time'] - pos_info['start_time']
        
        # Tạo clip từ frame
        clip = ImageClip(frame).set_duration(seg_duration).set_start(pos_info['start_time'])
        video_clips.append(clip)
    
    if show_progress:
        print()
    
    # Ghép các clips
    if show_progress:
        print("  Đang ghép video...")
    video = CompositeVideoClip(video_clips, size=(1920, 1080))
    
    # Set duration và audio
    video = video.set_duration(duration).set_audio(audio_clip)
    
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


def create_video(mp3_path, text_en, text_vi, output_folder, show_progress=True):
    """Tạo video MP4 từ audio và text (fallback nếu không có timestamps)"""
    if show_progress:
        print("\n🎬 Đang tạo video...")
    
    # Check xem có timestamps không
    timestamps_path = Path(mp3_path).parent / "timestamps.json"
    if timestamps_path.exists():
        if show_progress:
            print(f"✅ Tìm thấy timestamps.json - sử dụng sync chính xác!")
        timestamps = load_timestamps(timestamps_path)
        return create_video_with_timestamps(mp3_path, text_en, text_vi, timestamps, output_folder, show_progress)
    
    # Fallback: chia đều thời gian
    if show_progress:
        print("⚠️ Không tìm thấy timestamps.json - sử dụng chia đều thời gian")
        print("  Để sync chính xác hơn, chạy: python mp3_to_transcript_with_timestamps.py <mp3_path>")
    
    # Load audio
    audio_clip = AudioFileClip(mp3_path)
    duration = audio_clip.duration
    
    if show_progress:
        print(f"  Audio duration: {duration:.1f} seconds")
    
    # Chia text thành chunks (giảm chunk_size để sync tốt hơn với audio)
    chunks_en = split_text_into_chunks(text_en, chunk_size=200)
    chunks_vi = split_text_into_chunks(text_vi, chunk_size=200)
    
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
