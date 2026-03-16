#!/usr/bin/env python3
"""
EN + VI + Transcript + Timestamp to TXT
Kết hợp transcript tiếng Anh, tiếng Việt và timestamps từ Whisper
Tác giả: Script tự động
Ngày tạo: 2026-01-05
"""

import sys
import json
from pathlib import Path

# Tỷ lệ match tối thiểu giữa [AUTO] và [EN] (0-100)
# 30% cho word-level extraction
MATCH_PERCENT = 30


def read_transcript_file(file_path):
    """Đọc file transcript và trả về nội dung"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
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
        
        return content
    except FileNotFoundError:
        return None


def load_timestamps(json_path):
    """Load timestamps từ file JSON"""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            segments = json.load(f)
        return segments
    except FileNotFoundError:
        print(f"❌ Không tìm thấy file: {json_path}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Lỗi khi đọc JSON: {e}")
        return None


def format_timestamp(seconds):
    """Format giây thành HH:MM:SS,mmm"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def normalize_text(text):
    """Đơn giản hóa text để so sánh - chỉ giữ chữ cái (bao gồm Unicode)"""
    import re
    text = text.lower()
    # Giữ chữ cái (bao gồm Unicode cho tiếng Việt) và khoảng trắng
    # Xóa số, dấu câu, ký tự đặc biệt
    text = re.sub(r'[^\w\s]', '', text, flags=re.UNICODE)  # Xóa dấu câu
    text = re.sub(r'\d+', '', text)  # Xóa số
    text = re.sub(r'\s+', ' ', text)  # Chuẩn hóa khoảng trắng
    return text.strip()


def calculate_similarity(text1, text2):
    """Đo tương đồng giữa 2 text sử dụng word overlap và độ dài tương tự
    
    Trả về điểm từ 0-100 dựa trên:
    - Số từ trong text1 xuất hiện trong text2
    - Độ tương đồng về độ dài (ưu tiên text có độ dài gần bằng nhau)
    """
    from difflib import SequenceMatcher
    
    norm1 = normalize_text(text1)
    norm2 = normalize_text(text2)
    
    if not norm1 or not norm2:
        return 0.0
    
    words1 = norm1.split()
    words2 = norm2.split()
    words2_set = set(words2)
    
    if not words1:
        return 0.0
    
    # Đếm số từ trong text1 có trong text2
    matched_words = sum(1 for word in words1 if word in words2_set)
    
    # Tỷ lệ phần trăm từ khớp
    word_match_percent = (matched_words / len(words1)) * 100
    
    # Sequence similarity để xử lý thứ tự từ
    seq_ratio = SequenceMatcher(None, norm1, norm2).ratio() * 100
    
    # Tính độ tương đồng về độ dài (0-100)
    len1, len2 = len(words1), len(words2)
    length_ratio = min(len1, len2) / max(len1, len2) if max(len1, len2) > 0 else 0
    length_similarity = length_ratio * 100
    
    # Kết hợp: 50% word match + 15% sequence + 35% length similarity
    # Ưu tiên độ dài để [EN] khớp với [AUTO]
    return 0.5 * word_match_percent + 0.15 * seq_ratio + 0.35 * length_similarity


def split_into_sentences(text):
    """Chia text thành các chunks theo số từ (không phụ thuộc dấu câu)
    
    [AUTO] từ Whisper không ngắt theo câu mà ngắt bất kỳ,
    nên ta chia EN/VI thành các chunks nhỏ để match linh hoạt hơn
    """
    if not text:
        return []
    
    # Xóa xuống dòng, chuẩn hóa khoảng trắng
    text = text.replace('\n', ' ').strip()
    text = ' '.join(text.split())
    
    # Chia thành các từ
    words = text.split()
    
    if not words:
        return []
    
    # Chia thành các chunks nhỏ, mỗi chunk ~10 từ (non-overlapping)
    chunks = []
    chunk_size = 10
    
    for i in range(0, len(words), chunk_size):
        chunk = ' '.join(words[i:i + chunk_size])
        chunks.append(chunk)
    
    return chunks


def find_best_matching_sentence(segment_text, sentences, used_indices, start_index=0, original_words=None):
    """Tìm chunk hoặc nhóm chunks phù hợp nhất với segment text
    
    Sentences ở đây thực chất là các chunks (không phải câu nữa)
    Ưu tiên match 1:1, chỉ gộp chunks nếu segment dài
    
    Args:
        segment_text: Text từ Whisper segment
        sentences: List các chunks có thể
        used_indices: Set các index đã dùng
        start_index: Bắt đầu tìm từ index này (để maintain order)
        original_words: List tất cả các từ trong original text (để extract exact words)
    
    Returns:
        (best_indices, best_text, best_score) - indices là list các index chunks
    """
    if not sentences:
        return [], "", 0.0
    
    best_indices = []
    best_text = ""
    best_score = 0.0
    
    # Tính số từ trong segment để quyết định số chunks cần gộp
    segment_word_count = len(segment_text.split())
    
    # Ước lượng số chunks cần thiết (mỗi chunk ~10 từ)
    # Làm tròn lên để đảm bảo lấy đủ text
    estimated_chunks = (segment_word_count + 9) // 10  # Làm tròn lên
    max_chunks = min(3, max(1, estimated_chunks))  # Tối đa 3 chunks
    
    # Thử match với số chunks phù hợp (ưu tiên số chunks gần với estimated)
    for num_chunks in range(1, max_chunks + 1):
        for start_idx in range(start_index, len(sentences)):
            # Kiểm tra xem có thể lấy num_chunks từ start_idx không
            if start_idx + num_chunks > len(sentences):
                break
            
            # Kiểm tra các chunks này đã được dùng chưa
            indices = list(range(start_idx, start_idx + num_chunks))
            if any(idx in used_indices for idx in indices):
                continue
            
            # Gộp các chunks lại
            combined_text = ' '.join(sentences[idx] for idx in indices)
            
            # Tính similarity (0-100)
            score = calculate_similarity(segment_text, combined_text)
            
            # Bonus 10% cho chunk liền kề (maintain order)
            if start_idx == start_index:
                score += 10
            
            # Bonus cho match có số chunks gần với estimated (ưu tiên lấy đủ text)
            if num_chunks == estimated_chunks:
                score += 5
            elif num_chunks == 1:
                score += 3  # Vẫn ưu tiên đơn giản nhưng thấp hơn
            
            if score > best_score:
                best_score = score
                best_indices = indices
                best_text = combined_text
    
    # Nếu không tìm thấy match tốt từ start_index, quét lại từ đầu (chỉ 1 chunk)
    if not best_indices or best_score < MATCH_PERCENT:
        for start_idx in range(0, start_index):
            if start_idx in used_indices:
                continue
            
            score = calculate_similarity(segment_text, sentences[start_idx])
            
            if score > best_score:
                best_score = score
                best_indices = [start_idx]
                best_text = sentences[start_idx]
    
    # Nếu có original_words, extract exact words dựa trên indices và segment length
    # TẠM THỜI DISABLE để debug - chỉ dùng combined_text từ chunks
    # if best_indices and original_words:
    #     chunk_size = 10
    #     start_word_idx = best_indices[0] * chunk_size
    #     end_chunk_idx = best_indices[-1]
    #     
    #     # Tính end dựa trên segment length hoặc chunk boundary, tùy cái nào nhỏ hơn
    #     # Để tránh "ăn" text của segment sau
    #     end_by_segment = start_word_idx + segment_word_count
    #     end_by_chunks = (end_chunk_idx + 1) * chunk_size
    #     
    #     # Lấy max của 2 giá trị (ưu tiên segment length) nhưng +1-2 từ nếu cần
    #     end_word_idx = end_by_segment
    #     if end_by_segment < end_by_chunks:
    #         # Có thể lấy thêm 1-2 từ nếu còn trong chunk boundary
    #         end_word_idx = min(end_by_segment + 2, end_by_chunks)
    #     
    #     # Đảm bảo không vượt quá chiều dài original text
    #     end_word_idx = min(end_word_idx, len(original_words))
    #     
    #     # Extract exact words
    #     best_text = ' '.join(original_words[start_word_idx:end_word_idx])
    
    return best_indices, best_text, best_score


def match_segments_with_transcript(segments, en_text, vi_text):
    """Map từng segment với chunks tương ứng trong transcript EN và VI
    
    Sử dụng chunk-based matching (không phụ thuộc dấu câu) để phù hợp với
    cách Whisper ngắt segments (ngắt bất kỳ, không theo câu)
    
    Args:
        segments: List các segment từ Whisper (có start, end, text)
        en_text: Nội dung transcript tiếng Anh (có thể None)
        vi_text: Nội dung transcript tiếng Việt (có thể None)
    
    Returns:
        List các tuple (segment, en_chunk, vi_chunk)
    """
    # Chuẩn hóa và split thành words
    en_words = en_text.replace('\n', ' ').split() if en_text else []
    vi_words = vi_text.replace('\n', ' ').split() if vi_text else []
    
    # Chia transcript thành các chunks (~10 từ/chunk) - chỉ để hiển thị stats
    en_chunks = split_into_sentences(en_text) if en_text else []
    vi_chunks = split_into_sentences(vi_text) if vi_text else []
    
    print(f"  📊 Whisper segments: {len(segments)}, EN words: {len(en_words)}, VI words: {len(vi_words)}")
    
    matched = []
    
    # Nếu không có transcript, trả về segments với chunk rỗng
    if not en_words and not vi_words:
        for seg in segments:
            matched.append((seg, "", ""))
        return matched
    
    # Track word indices để maintain order và tránh overlap
    next_en_word_idx = 0  # Track ở word level
    next_vi_idx = 0
    
    # Map từng segment với chunk EN và VI
    for seg in segments:
        seg_text = seg['text']
        segment_word_count = len(seg_text.split())
        
        # Tìm EN text: extract exact words từ next_en_word_idx
        en_chunk = ""
        if en_words and next_en_word_idx < len(en_words):
            # Lấy đúng số từ cần thiết (exact match với [AUTO])
            end_word_idx = min(next_en_word_idx + segment_word_count, len(en_words))
            en_chunk = ' '.join(en_words[next_en_word_idx:end_word_idx])
            
            # Verify matching quality bằng similarity score
            similarity = calculate_similarity(seg_text, en_chunk)
            if similarity >= MATCH_PERCENT:
                # Accept match và update next position
                next_en_word_idx = end_word_idx
            else:
                # Không match tốt, không dùng
                en_chunk = ""
        
        # Tìm VI text: tương tự EN, extract exact words
        vi_chunk = ""
        if vi_words and next_vi_idx < len(vi_words):
            # VI text thường dài hơn EN, estimate ~1.2x words
            vi_word_count = int(segment_word_count * 1.3)
            end_vi_idx = min(next_vi_idx + vi_word_count, len(vi_words))
            vi_chunk = ' '.join(vi_words[next_vi_idx:end_vi_idx])
            next_vi_idx = end_vi_idx
        
        matched.append((seg, en_chunk, vi_chunk))
    
    # Thống kê matching với điểm số
    matched_en = sum(1 for _, en, _ in matched if en)
    matched_vi = sum(1 for _, _, vi in matched if vi)
    print(f"  ✅ Matched: {matched_en}/{len(segments)} EN ({matched_en*100//len(segments)}%), {matched_vi}/{len(segments)} VI ({matched_vi*100//len(segments)}%)")
    print(f"  🎯 Match threshold: EN={MATCH_PERCENT}% (VI mapped by position)")
    
    return matched


def save_combined_output(matched_data, output_path):
    """Lưu output kết hợp [AUTO], [EN], [VI]"""
    with open(output_path, 'w', encoding='utf-8') as f:
        # Thêm header với thông tin config
        f.write(f"# Match Threshold: EN={MATCH_PERCENT}% (VI mapped by position)\n")
        f.write(f"# Generated: {output_path.name}\n")
        f.write("#" + "="*60 + "\n\n")
        
        for i, (seg, en_part, vi_part) in enumerate(matched_data, 1):
            start_time = format_timestamp(seg['start'])
            end_time = format_timestamp(seg['end'])
            
            f.write(f"{i}\n")
            f.write(f"{start_time} --> {end_time}\n")
            f.write(f"[AUTO] {seg['text']}\n")
            
            if en_part:
                f.write(f"[EN] {en_part}\n")
            else:
                f.write(f"[EN] (no match >= {MATCH_PERCENT}%)\n")
                
            if vi_part:
                f.write(f"[VI] {vi_part}\n")
            else:
                f.write(f"[VI] (not available)\n")
            
            f.write("\n")
    
    print(f"✅ Đã lưu output: {output_path}")


def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python en+vi+transcript+timestamp__to_txt.py <folder_path>")
        print("\nFolder phải chứa:")
        print("  - timestamps.json (từ Whisper)")
        print("  - transcript.txt (tiếng Anh)")
        print("  - transcript_vietnamese.txt (tiếng Việt)")
        sys.exit(1)
    
    folder_path = Path(sys.argv[1])
    
    if not folder_path.exists():
        print(f"❌ Folder không tồn tại: {folder_path}")
        sys.exit(1)
    
    # Load files
    print("\n📂 Đang đọc files...")
    
    timestamps_file = folder_path / "timestamps.json"
    en_file = folder_path / "transcript.txt"
    vi_file = folder_path / "transcript_vietnamese.txt"
    
    segments = load_timestamps(timestamps_file)
    if not segments:
        sys.exit(1)
    print(f"  ✅ Đã load {len(segments)} segments từ {timestamps_file.name}")
    
    en_text = read_transcript_file(en_file)
    if en_text:
        print(f"  ✅ Đã đọc transcript EN: {len(en_text)} ký tự")
    else:
        print(f"  ⚠️ Không tìm thấy {en_file.name}")
    
    vi_text = read_transcript_file(vi_file)
    if vi_text:
        print(f"  ✅ Đã đọc transcript VI: {len(vi_text)} ký tự")
    else:
        print(f"  ⚠️ Không tìm thấy {vi_file.name}")
    
    # Match segments với transcripts
    print("\n🔗 Đang map segments với transcripts...")
    matched_data = match_segments_with_transcript(segments, en_text, vi_text)
    print(f"  ✅ Đã map {len(matched_data)} segments")
    
    # Save output
    output_file = folder_path / "transcript_with_en+vi_with_timestamps.txt"
    save_combined_output(matched_data, output_file)
    
    print(f"\n✅ Hoàn thành!")
    print(f"  Output: {output_file}")


if __name__ == "__main__":
    main()
