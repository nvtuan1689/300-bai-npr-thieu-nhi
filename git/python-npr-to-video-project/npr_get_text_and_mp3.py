#!/usr/bin/env python3
"""
NPR Article Scraper - Lấy transcript và audio từ các bài viết NPR
Tác giả: Script tự động
Ngày tạo: 2026-01-01
"""

import os
import sys
import json
import re
from datetime import datetime
from pathlib import Path
import requests
from bs4 import BeautifulSoup


# Lưu input history vào trong file này dưới dạng comment
# HISTORY_START
LAST_INPUTS = {
    "url": ""
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
    print("NPR ARTICLE SCRAPER - Lấy transcript và audio từ NPR")
    print("=" * 70)
    print()
    
    # Lấy URL
    last_url = get_last_input("url")
    if last_url:
        print(f"URL lần trước: {last_url}")
    
    url = input("Nhập URL của bài viết NPR (hoặc Enter để dùng URL lần trước): ").strip()
    
    if not url and last_url:
        url = last_url
        print(f"Sử dụng URL: {url}")
    elif not url:
        print("❌ URL không được để trống!")
        sys.exit(1)
    
    # Validate URL
    if not url.startswith("http"):
        print("❌ URL không hợp lệ! URL phải bắt đầu bằng http hoặc https")
        sys.exit(1)
    
    # Lưu input
    save_last_input("url", url)
    
    return url


def create_output_folder():
    """Tạo folder output theo format ngày giờ"""
    now = datetime.now()
    folder_name = now.strftime("%Y_%m_%d__%H_%M")
    folder_path = Path(folder_name)
    folder_path.mkdir(exist_ok=True)
    print(f"✅ Đã tạo folder: {folder_name}")
    return folder_path


def download_webpage(url, folder_path):
    """Download trang web"""
    print(f"\n📥 Đang tải trang web từ: {url}")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Lưu HTML
        html_file = folder_path / "page.html"
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        print(f"✅ Đã lưu trang web: {html_file}")
        return response.text
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Lỗi khi tải trang web: {e}")
        sys.exit(1)


def extract_title_and_transcript(html_content):
    """Trích xuất title và transcript từ HTML"""
    print("\n📝 Đang trích xuất title và transcript...")
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Tìm title - có nhiều cách
    title = None
    
    # Cách 1: Tìm trong h1 class="transcript"
    title_h1 = soup.find('h1', class_='transcript')
    if title_h1:
        title = title_h1.get_text(strip=True)
        # Loại bỏ ký tự < và khoảng trắng đầu
        title = re.sub(r'^<\s*', '', title)
    
    # Cách 2: Tìm trong meta tag
    if not title:
        title_meta = soup.find('meta', property='og:title')
        if title_meta:
            title = title_meta.get('content', '').strip()
    
    # Cách 3: Tìm trong input hidden
    if not title:
        title_input = soup.find('input', id=lambda x: x and x.startswith('title'))
        if title_input:
            title = title_input.get('value', '').strip()
    
    # Tìm transcript - tìm phần có class chứa "transcript"
    transcript = ""
    
    # Tìm div có class="transcript"
    transcript_div = soup.find('div', class_='transcript')
    
    if transcript_div:
        # Lấy tất cả p tags trong div này
        paragraphs = transcript_div.find_all('p', recursive=False)
        transcript_parts = []
        
        for p in paragraphs:
            text = p.get_text(strip=True)
            # Bỏ qua các đoạn rỗng
            if text and text not in transcript_parts:
                transcript_parts.append(text)
        
        transcript = '\n\n'.join(transcript_parts)
    
    # Nếu không tìm thấy, thử cách khác
    if not transcript:
        article = soup.find('article')
        if article:
            # Tìm tất cả p tags
            paragraphs = article.find_all('p')
            transcript_parts = []
            seen_texts = set()  # Để tránh trùng lặp
            in_transcript = False
            
            for p in paragraphs:
                text = p.get_text(strip=True)
                
                # Bắt đầu khi gặp HOST: hoặc BYLINE:
                if ('HOST:' in text or 'BYLINE:' in text) and not in_transcript:
                    in_transcript = True
                
                if in_transcript:
                    # Chỉ thêm nếu chưa có trong set (tránh trùng lặp)
                    if text and text not in seen_texts:
                        # Bỏ qua các disclaimer
                        if 'Copyright ©' in text or 'NPR.  All rights reserved' in text:
                            break
                        
                        transcript_parts.append(text)
                        seen_texts.add(text)
                    
                    # Kết thúc khi gặp "Thank you" và đã có đủ nội dung
                    if 'Thank you' in text and len(transcript_parts) > 10:
                        break
            
            transcript = '\n\n'.join(transcript_parts)
    
    if not title:
        print("⚠️ Không tìm thấy title")
        title = "No title found"
    else:
        print(f"✅ Title: {title}")
    
    if not transcript:
        print("⚠️ Không tìm thấy transcript")
    else:
        print(f"✅ Transcript: {len(transcript)} ký tự")
    
    return title, transcript


def download_audio(html_content, folder_path):
    """Tìm và download file audio MP3"""
    print("\n🎵 Đang tìm và tải audio...")
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Tìm audio URL
    audio_url = None
    
    # Cách 1: Tìm trong link download
    download_link = soup.find('a', href=re.compile(r'\.mp3'))
    if download_link:
        audio_url = download_link.get('href')
    
    # Cách 2: Tìm trong data attribute
    if not audio_url:
        audio_data = soup.find(attrs={'data-audio': True})
        if audio_data:
            # Parse JSON data
            try:
                audio_info = json.loads(audio_data.get('data-audio', '{}'))
                audio_url = audio_info.get('audioUrl') or audio_info.get('url')
            except:
                pass
    
    # Cách 3: Tìm bằng regex trong toàn bộ HTML
    if not audio_url:
        mp3_pattern = r'https?://[^\s<>"]+?\.mp3[^\s<>"]*'
        matches = re.findall(mp3_pattern, html_content)
        if matches:
            # Lấy URL đầu tiên có chứa "npr" hoặc "ondemand"
            for match in matches:
                if 'npr' in match.lower() or 'ondemand' in match.lower():
                    audio_url = match
                    # Clean URL - loại bỏ các ký tự escape
                    audio_url = audio_url.replace('\\', '')
                    break
    
    if not audio_url:
        print("⚠️ Không tìm thấy audio URL")
        return None
    
    print(f"🔗 Audio URL: {audio_url}")
    
    # Download audio
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(audio_url, headers=headers, timeout=60, stream=True)
        response.raise_for_status()
        
        audio_file = folder_path / "audio.mp3"
        
        # Download với progress
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        
        with open(audio_file, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        print(f"\r⏳ Đang tải: {percent:.1f}%", end='')
        
        print(f"\n✅ Đã lưu audio: {audio_file} ({downloaded / 1024 / 1024:.2f} MB)")
        return audio_file
    
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Lỗi khi tải audio: {e}")
        return None


def save_transcript(title, transcript, folder_path):
    """Lưu title và transcript vào file txt"""
    print("\n💾 Đang lưu transcript...")
    
    txt_file = folder_path / "transcript.txt"
    
    # Loại bỏ phần copyright disclaimer
    copyright_markers = [
        'Copyright ©',
        'NPR.  All rights reserved',
        'Accuracy and availability of NPR transcripts',
        'The authoritative record of NPR'
    ]
    
    # Tìm vị trí của copyright
    copyright_index = -1
    for marker in copyright_markers:
        idx = transcript.find(marker)
        if idx != -1:
            copyright_index = idx
            break
    
    # Cắt bỏ phần copyright
    if copyright_index != -1:
        transcript = transcript[:copyright_index].strip()
    
    # Format lại: xuống dòng trước mỗi speaker (CHỮ HOA + : + khoảng cách)
    # Pattern: tìm các chữ cái in hoa + dấu: + space (ví dụ: "TREISMAN: ")
    # Thêm \n\n trước speaker name nếu không có newline
    transcript = re.sub(r'([a-z.,!?;)\]])([A-Z]{2,}:)\s', r'\1\n\n\2 ', transcript)
    
    # Loại bỏ tất cả các dòng trống liên tiếp (chỉ giữ 1 dòng trống)
    transcript = re.sub(r'\n\s*\n', '\n\n', transcript)
    
    # Loại bỏ 2+ dòng trống liên tiếp
    transcript = re.sub(r'\n{3,}', '\n\n', transcript)
    transcript = transcript.strip()
    
    with open(txt_file, 'w', encoding='utf-8') as f:
        f.write(f"TITLE: {title}\n")
        f.write("=" * 70 + "\n")
        f.write(transcript)
    
    print(f"✅ Đã lưu transcript: {txt_file}")
    return txt_file


def main():
    """Main function"""
    try:
        # Lấy input
        url = get_user_input()
        
        # Tạo folder output
        folder_path = create_output_folder()
        
        # Download trang web
        html_content = download_webpage(url, folder_path)
        
        # Trích xuất title và transcript
        title, transcript = extract_title_and_transcript(html_content)
        
        # Lưu transcript
        save_transcript(title, transcript, folder_path)
        
        # Download audio
        download_audio(html_content, folder_path)
        
        print("\n" + "=" * 70)
        print("✅ HOÀN THÀNH!")
        print(f"📁 Tất cả file đã được lưu vào: {folder_path}")
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
