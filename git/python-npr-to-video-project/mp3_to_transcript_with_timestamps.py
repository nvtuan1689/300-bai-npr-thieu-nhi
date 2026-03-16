#!/usr/bin/env python3
"""
MP3 to Transcript with Timestamps - Sử dụng Whisper AI (offline)
Tác giả: Script tự động
Ngày tạo: 2026-01-02

Tạo transcript với timestamps chính xác từ audio MP3 sử dụng Whisper AI
"""

import sys
import json
from pathlib import Path


def transcribe_audio_with_timestamps(mp3_path, model_size="base", language="en"):
    """
    Transcribe audio và tạo timestamps
    
    Args:
        mp3_path: Path đến file MP3
        model_size: Kích thước model Whisper (tiny, base, small, medium, large)
        language: Ngôn ngữ (en, vi, etc.)
    
    Returns:
        segments: List các segment với text và timestamps
    """
    print(f"\n🎙️ Đang transcribe audio với Whisper AI (model: {model_size})...")
    
    try:
        import whisper
        import torch
        
        # Load model với weights_only=False để tương thích PyTorch 2.6
        print(f"  Đang load model '{model_size}'...")
        
        # Monkey patch torch.load để fix PyTorch 2.6 compatibility
        original_load = torch.load
        def patched_load(*args, **kwargs):
            kwargs['weights_only'] = False
            return original_load(*args, **kwargs)
        torch.load = patched_load
        
        model = whisper.load_model(model_size)
        
        # Restore original torch.load
        torch.load = original_load
        
        # Transcribe
        print(f"  Đang transcribe: {mp3_path}")
        print(f"  ⏳ Quá trình này có thể mất vài phút...")
        
        result = model.transcribe(
            str(mp3_path),
            language=language,
            verbose=False,
            word_timestamps=False
        )
        
        # Extract segments
        segments = []
        for segment in result['segments']:
            segments.append({
                'start': segment['start'],
                'end': segment['end'],
                'text': segment['text'].strip()
            })
        
        print(f"✅ Đã transcribe: {len(segments)} segments")
        
        return segments
    
    except ImportError:
        print("❌ Thư viện 'openai-whisper' chưa được cài đặt!")
        print("  Cài đặt: pip install openai-whisper")
        sys.exit(1)
    except FileNotFoundError as e:
        print(f"❌ Lỗi: Không tìm thấy file hoặc thiếu ffmpeg!")
        print(f"  Chi tiết: {e}")
        print("\n💡 Giải pháp:")
        print(f"  1. Kiểm tra file MP3 có tồn tại: {mp3_path}")
        print("  2. Cài đặt ffmpeg:")
        print("     - Download: https://ffmpeg.org/download.html")
        print("     - Hoặc: https://github.com/BtbN/FFmpeg-Builds/releases")
        print("     - Thêm ffmpeg.exe vào PATH hoặc folder hiện tại")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Lỗi khi transcribe: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def save_segments_to_json(segments, output_path):
    """Lưu segments vào file JSON"""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(segments, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Đã lưu timestamps: {output_path}")


def save_segments_to_txt(segments, output_path):
    """Lưu segments vào file TXT (dạng SRT)"""
    with open(output_path, 'w', encoding='utf-8') as f:
        for i, seg in enumerate(segments, 1):
            start_time = format_timestamp(seg['start'])
            end_time = format_timestamp(seg['end'])
            f.write(f"{i}\n")
            f.write(f"{start_time} --> {end_time}\n")
            f.write(f"{seg['text']}\n\n")
    
    print(f"✅ Đã lưu transcript: {output_path}")


def format_timestamp(seconds):
    """Format giây thành HH:MM:SS,mmm"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def main():
    """Main function - standalone usage"""
    if len(sys.argv) < 2:
        print("Usage: python mp3_to_transcript_with_timestamps.py <mp3_path> [model_size]")
        print("Model sizes: tiny, base, small, medium, large")
        print("  tiny  - Nhanh nhất, ít chính xác (~1GB RAM)")
        print("  base  - Cân bằng (recommended, ~1GB RAM)")
        print("  small - Chính xác hơn (~2GB RAM)")
        print("  medium - Rất chính xác (~5GB RAM)")
        print("  large - Chính xác nhất (~10GB RAM)")
        sys.exit(1)
    
    mp3_path = sys.argv[1]
    model_size = sys.argv[2] if len(sys.argv) > 2 else "base"
    
    # Validate file
    if not Path(mp3_path).exists():
        print(f"❌ File không tồn tại: {mp3_path}")
        sys.exit(1)
    
    # Transcribe
    segments = transcribe_audio_with_timestamps(mp3_path, model_size=model_size)
    
    # Save outputs
    mp3_file = Path(mp3_path)
    output_folder = mp3_file.parent
    
    json_path = output_folder / "timestamps.json"
    txt_path = output_folder / "transcript_with_timestamps.txt"
    
    save_segments_to_json(segments, json_path)
    save_segments_to_txt(segments, txt_path)
    
    print(f"\n✅ Hoàn thành!")
    print(f"  JSON: {json_path}")
    print(f"  TXT: {txt_path}")


if __name__ == "__main__":
    main()
