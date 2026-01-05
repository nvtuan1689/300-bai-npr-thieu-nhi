#!/usr/bin/env python3
"""
Text to Vietnamese Translator - Dịch text sang tiếng Việt
Tác giả: Script tự động
Ngày tạo: 2026-01-02
"""

import sys


def translate_text(text, show_progress=True):
    """Dịch text sang tiếng Việt"""
    if show_progress:
        print("\n🌐 Đang dịch sang tiếng Việt...")
    
    try:
        from deep_translator import GoogleTranslator
        
        # Chia text thành các đoạn nhỏ (Google Translate có giới hạn)
        max_length = 4500
        paragraphs = text.split('\n\n')
        translated_paragraphs = []
        
        translator = GoogleTranslator(source='en', target='vi')
        
        # Dịch từng paragraph riêng biệt để giữ nguyên format xuống dòng
        for i, para in enumerate(paragraphs):
            if not para.strip():  # Bỏ qua paragraph rỗng
                translated_paragraphs.append("")
                continue
                
            if show_progress:
                print(f"  Đang dịch đoạn {i + 1}/{len(paragraphs)}...")
            
            # Dịch từng paragraph một để giữ format
            translated = translator.translate(para.strip())
            translated_paragraphs.append(translated)
        
        # Join lại với \n\n để giữ nguyên structure
        vietnamese_text = '\n\n'.join(translated_paragraphs)
        
        if show_progress:
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


def main():
    """Main function - standalone usage"""
    if len(sys.argv) < 2:
        print("Usage: python text_to_vietnamese.py <path_to_txt_file>")
        sys.exit(1)
    
    txt_path = sys.argv[1]
    
    # Đọc transcript
    text_en = read_transcript(txt_path)
    
    # Dịch sang tiếng Việt
    text_vi = translate_text(text_en)
    
    # Lưu bản dịch
    vi_path = save_vietnamese_text(text_vi, txt_path)
    
    print(f"\n✅ Hoàn thành! Đã lưu: {vi_path}")


if __name__ == "__main__":
    main()
