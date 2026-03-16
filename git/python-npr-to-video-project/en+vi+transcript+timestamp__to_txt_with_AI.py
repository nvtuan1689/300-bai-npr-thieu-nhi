"""
Script map [AUTO], [EN], [VI] transcripts sử dụng AI semantic similarity
Sử dụng Sentence Transformers để matching dựa trên ngữ cảnh thay vì string matching

Requirements:
    pip install sentence-transformers torch

Model: paraphrase-multilingual-MiniLM-L12-v2 (~420MB)
- Hỗ trợ 50+ ngôn ngữ (bao gồm English và Vietnamese)
- Offline sau khi download lần đầu
- Semantic matching dựa trên context
"""

import json
from pathlib import Path
import sys
import numpy as np

try:
    from sentence_transformers import SentenceTransformer, util
except ImportError:
    print("❌ Chưa cài đặt sentence-transformers!")
    print("   Chạy: pip install sentence-transformers torch")
    sys.exit(1)

# Cấu hình
MATCH_THRESHOLD = 0.35  # Cosine similarity threshold (0-1), 0.35 = 35%
MODEL_NAME = 'paraphrase-multilingual-MiniLM-L12-v2'  # Multilingual model


def seconds_to_timestamp(seconds):
    """Chuyển seconds thành timestamp format SRT"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def read_transcript_file(file_path):
    """Đọc file transcript và trả về nội dung"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return None


def split_into_sentences(text):
    """Chia text thành các chunks nhỏ (~10-15 từ) để matching linh hoạt"""
    if not text:
        return []
    
    text = text.replace('\n', ' ').strip()
    text = ' '.join(text.split())
    words = text.split()
    
    if not words:
        return []
    
    # Chia thành chunks 12 từ
    chunks = []
    chunk_size = 12
    
    for i in range(0, len(words), chunk_size):
        chunk = ' '.join(words[i:i + chunk_size])
        chunks.append(chunk)
    
    return chunks


def find_best_match_with_ai(segment_text, candidates, model, used_indices, start_index=0):
    """
    Tìm chunk phù hợp nhất sử dụng AI semantic similarity
    
    Args:
        segment_text: Text từ Whisper segment [AUTO]
        candidates: List các chunks có thể (EN hoặc VI)
        model: Sentence Transformer model
        used_indices: Set các index đã dùng
        start_index: Bắt đầu tìm từ index này
    
    Returns:
        (best_index, best_text, best_score)
    """
    if not candidates:
        return None, "", 0.0
    
    # Encode segment text
    segment_embedding = model.encode(segment_text, convert_to_tensor=True)
    
    best_index = None
    best_text = ""
    best_score = 0.0
    
    # Thử match với 1-2 chunks liên tiếp
    for num_chunks in [1, 2]:
        for idx in range(start_index, len(candidates)):
            # Kiểm tra có thể lấy num_chunks không
            if idx + num_chunks > len(candidates):
                break
            
            # Kiểm tra đã dùng chưa
            indices = list(range(idx, idx + num_chunks))
            if any(i in used_indices for i in indices):
                continue
            
            # Gộp chunks
            combined_text = ' '.join(candidates[i] for i in indices)
            
            # Tính semantic similarity
            candidate_embedding = model.encode(combined_text, convert_to_tensor=True)
            similarity = util.cos_sim(segment_embedding, candidate_embedding).item()
            
            # Bonus cho chunk liền kề (maintain order)
            if idx == start_index:
                similarity += 0.05
            
            if similarity > best_score:
                best_score = similarity
                best_index = idx
                best_text = combined_text
    
    return best_index, best_text, best_score


def match_segments_with_ai(segments, en_text, vi_text, model):
    """
    Map segments với transcripts sử dụng AI semantic matching
    
    Args:
        segments: List các Whisper segments
        en_text: Transcript English
        vi_text: Transcript Vietnamese
        model: Sentence Transformer model
    
    Returns:
        List (segment, en_match, vi_match)
    """
    # Chia thành chunks
    en_chunks = split_into_sentences(en_text) if en_text else []
    vi_chunks = split_into_sentences(vi_text) if vi_text else []
    
    # Prepare word arrays cho extraction
    en_words = en_text.replace('\n', ' ').split() if en_text else []
    vi_words = vi_text.replace('\n', ' ').split() if vi_text else []
    
    print(f"  📊 Segments: {len(segments)}, EN chunks: {len(en_chunks)}, VI chunks: {len(vi_chunks)}")
    print(f"  🤖 Đang matching với AI model: {MODEL_NAME}")
    
    matched = []
    used_en_indices = set()
    used_vi_indices = set()
    next_en_idx = 0
    next_vi_idx = 0
    
    # Track word-level positions
    next_en_word_idx = 0
    next_vi_word_idx = 0
    
    for i, seg in enumerate(segments):
        seg_text = seg['text']
        segment_word_count = len(seg_text.split())
        
        # Match EN với AI
        en_chunk = ""
        en_score = 0.0
        
        if en_words and next_en_word_idx < len(en_words):
            # Extract candidate window (2x segment length để có nhiều options)
            window_size = segment_word_count * 2
            end_window = min(next_en_word_idx + window_size, len(en_words))
            candidate_text = ' '.join(en_words[next_en_word_idx:end_window])
            
            # Tính similarity với window này
            seg_emb = model.encode(seg_text, convert_to_tensor=True)
            cand_emb = model.encode(candidate_text, convert_to_tensor=True)
            similarity = util.cos_sim(seg_emb, cand_emb).item()
            
            if similarity >= MATCH_THRESHOLD:
                # Extract exact words cần thiết
                end_word_idx = min(next_en_word_idx + segment_word_count, len(en_words))
                en_chunk = ' '.join(en_words[next_en_word_idx:end_word_idx])
                en_score = similarity
                next_en_word_idx = end_word_idx
        
        # Match VI với AI (similar approach)
        vi_chunk = ""
        vi_score = 0.0
        
        if vi_words and next_vi_word_idx < len(vi_words):
            # VI thường dài hơn EN ~1.3-1.5x
            vi_word_count = int(segment_word_count * 1.3)
            window_size = vi_word_count * 2
            end_window = min(next_vi_word_idx + window_size, len(vi_words))
            candidate_text = ' '.join(vi_words[next_vi_word_idx:end_window])
            
            # Tính similarity
            seg_emb = model.encode(seg_text, convert_to_tensor=True)
            cand_emb = model.encode(candidate_text, convert_to_tensor=True)
            similarity = util.cos_sim(seg_emb, cand_emb).item()
            
            if similarity >= MATCH_THRESHOLD * 0.7:  # Lower threshold cho VI (cross-language)
                end_vi_idx = min(next_vi_word_idx + vi_word_count, len(vi_words))
                vi_chunk = ' '.join(vi_words[next_vi_word_idx:end_vi_idx])
                vi_score = similarity
                next_vi_word_idx = end_vi_idx
        
        matched.append((seg, en_chunk, vi_chunk))
        
        # Progress indicator
        if (i + 1) % 10 == 0:
            print(f"    Processed {i+1}/{len(segments)} segments...")
    
    # Stats
    matched_en = sum(1 for _, en, _ in matched if en)
    matched_vi = sum(1 for _, _, vi in matched if vi)
    print(f"  ✅ Matched: {matched_en}/{len(segments)} EN ({matched_en*100//len(segments)}%), "
          f"{matched_vi}/{len(segments)} VI ({matched_vi*100//len(segments)}%)")
    print(f"  🎯 Threshold: EN={MATCH_THRESHOLD:.1%}, VI={MATCH_THRESHOLD*0.7:.1%}")
    
    return matched


def main():
    if len(sys.argv) < 2:
        print("Usage: python en+vi+transcript+timestamp__to_txt_with_AI.py <folder_name>")
        print("Example: python en+vi+transcript+timestamp__to_txt_with_AI.py 2026_01_05__21_19")
        sys.exit(1)
    
    folder_name = sys.argv[1]
    folder_path = Path(folder_name)
    
    if not folder_path.exists():
        print(f"❌ Không tìm thấy folder: {folder_path}")
        sys.exit(1)
    
    print("📂 Đang đọc files...")
    
    # Load Whisper segments
    timestamps_file = folder_path / "timestamps.json"
    if not timestamps_file.exists():
        print(f"❌ Không tìm thấy {timestamps_file}")
        sys.exit(1)
    
    with open(timestamps_file, 'r', encoding='utf-8') as f:
        segments = json.load(f)
    print(f"  ✅ Đã load {len(segments)} segments từ timestamps.json")
    
    # Load transcripts
    en_file = folder_path / "transcript.txt"
    vi_file = folder_path / "transcript_vietnamese.txt"
    
    en_text = read_transcript_file(en_file)
    vi_text = read_transcript_file(vi_file)
    
    if en_text:
        print(f"  ✅ Đã đọc transcript EN: {len(en_text)} ký tự")
    if vi_text:
        print(f"  ✅ Đã đọc transcript VI: {len(vi_text)} ký tự")
    
    # Load AI model
    print(f"\n🤖 Đang load AI model: {MODEL_NAME}")
    print("   (Lần đầu sẽ download ~420MB, sau đó dùng offline)")
    
    try:
        model = SentenceTransformer(MODEL_NAME)
        print("  ✅ Model loaded successfully!")
    except Exception as e:
        print(f"  ❌ Lỗi load model: {e}")
        sys.exit(1)
    
    # Match segments với AI
    print(f"\n🔗 Đang map segments với AI semantic matching...")
    matched = match_segments_with_ai(segments, en_text, vi_text, model)
    print(f"  ✅ Đã map {len(matched)} segments")
    
    # Write output
    output_file = folder_path / "transcript_with_en+vi_with_timestamps_AI.txt"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"# AI Matching with {MODEL_NAME}\n")
        f.write(f"# Threshold: EN={MATCH_THRESHOLD:.1%}, VI={MATCH_THRESHOLD*0.7:.1%}\n")
        f.write(f"# Generated: transcript_with_en+vi_with_timestamps_AI.txt\n")
        f.write("#" + "="*60 + "\n\n")
        
        for idx, (seg, en_chunk, vi_chunk) in enumerate(matched, 1):
            start_time = seconds_to_timestamp(seg['start'])
            end_time = seconds_to_timestamp(seg['end'])
            
            f.write(f"{idx}\n")
            f.write(f"{start_time} --> {end_time}\n")
            f.write(f"[AUTO] {seg['text']}\n")
            
            if en_chunk:
                f.write(f"[EN] {en_chunk}\n")
            else:
                f.write(f"[EN] (no match)\n")
            
            if vi_chunk:
                f.write(f"[VI] {vi_chunk}\n")
            else:
                f.write(f"[VI] (no match)\n")
            
            f.write("\n")
    
    print(f"✅ Đã lưu output: {output_file}")
    print(f"\n✅ Hoàn thành!")
    print(f"  Output: {output_file}")


if __name__ == "__main__":
    main()
