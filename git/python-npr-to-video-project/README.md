# NPR Article Scraper

Script Python để tải transcript và audio từ các bài viết NPR.

## Yêu cầu

- Python 3.7+
- Các thư viện: requests, beautifulsoup4, lxml

## Cài đặt

```bash
pip install -r requirements.txt
```

## Sử dụng

### Cách 1: Chạy trực tiếp

```bash
python npr_get_text_and_mp3.py
```

Script sẽ:
1. Hỏi bạn nhập URL của bài viết NPR (ví dụ: https://www.npr.org/transcripts/nx-s1-5655252)
2. Tạo folder mới theo format `YYYY_MM_DD__HH_MM`
3. Tải trang web và lưu vào `page.html`
4. Trích xuất title và transcript, lưu vào `transcript.txt`
5. Tìm và tải audio file, lưu vào `audio.mp3`

### Cách 2: Sử dụng Virtual Environment (khuyến nghị)

```bash
# Tạo virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (Linux/Mac)
source .venv/bin/activate

# Cài đặt packages
pip install -r requirements.txt

# Chạy script
python npr_get_text_and_mp3.py
```

### Cách 3: Test chức năng

```bash
# Chạy demo test
python demo_test.py
```

## Tính năng

- **Ghi nhớ URL cuối cùng**: Script tự động lưu URL bạn đã nhập để gợi ý cho lần chạy tiếp theo
- **Tự động tạo folder**: Mỗi lần chạy tạo folder mới với timestamp
- **Download progress**: Hiển thị tiến độ download audio
- **Error handling**: Xử lý lỗi một cách rõ ràng

## Cấu trúc output

```
2025_12_31__22_15/
├── page.html          # Trang web gốc
├── transcript.txt     # Title và transcript (không có HTML)
└── audio.mp3         # File audio
```

## Ví dụ

```
NPR ARTICLE SCRAPER - Lấy transcript và audio từ NPR
======================================================================

URL lần trước: https://www.npr.org/transcripts/nx-s1-5655252
Nhập URL của bài viết NPR (hoặc Enter để dùng URL lần trước):
Sử dụng URL: https://www.npr.org/transcripts/nx-s1-5655252
✅ Đã tạo folder: 2025_12_31__22_15

📥 Đang tải trang web từ: https://www.npr.org/transcripts/nx-s1-5655252
✅ Đã lưu trang web: 2025_12_31__22_15\page.html

📝 Đang trích xuất title và transcript...
✅ Title: Farmers are about to pay a lot more for health insurance
✅ Transcript: 5234 ký tự

💾 Đang lưu transcript...
✅ Đã lưu transcript: 2025_12_31__22_15\transcript.txt

🎵 Đang tìm và tải audio...
🔗 Audio URL: https://ondemand.npr.org/...
⏳ Đang tải: 100.0%
✅ Đã lưu audio: 2025_12_31__22_15\audio.mp3 (3.58 MB)

======================================================================
✅ HOÀN THÀNH!
📁 Tất cả file đã được lưu vào: 2025_12_31__22_15
======================================================================
```

## Ghi chú

- Script tự động lưu URL bạn đã nhập vào chính file script để gợi ý cho lần sau
- Nếu không tìm thấy audio, script vẫn tiếp tục và lưu transcript
- Hỗ trợ các định dạng URL NPR khác nhau
