# MP3 và Text to MP4 Converter

Script Python để tạo video MP4 từ file audio MP3 và transcript text, với phụ đề song ngữ (Anh-Việt).

## Tính năng

- ✅ Nhập path đến file MP3 và TXT
- ✅ Tự động dịch transcript sang tiếng Việt
- ✅ Tạo video MP4 với:
  - Audio từ file MP3
  - Text tiếng Anh bên trái
  - Text tiếng Việt bên phải
  - Highlight đoạn đang đọc
- ✅ Lưu input history để sử dụng lại

## Yêu cầu

- Python 3.7+
- Thư viện: moviepy, deep-translator, Pillow, numpy

## Cài đặt

```bash
pip install -r requirements.txt
```

**Lưu ý quan trọng:** 
- MoviePy yêu cầu **ffmpeg** để render video
- Download ffmpeg từ: https://ffmpeg.org/download.html
- Thêm ffmpeg vào PATH hoặc đặt trong cùng folder

### Cài đặt ffmpeg (Windows)

1. Download ffmpeg từ: https://github.com/BtbN/FFmpeg-Builds/releases
2. Giải nén và copy `ffmpeg.exe` vào folder dự án
3. Hoặc thêm folder ffmpeg vào PATH

## Sử dụng

### Cách 1: Chạy trực tiếp

```bash
python mp3_and_text_to_mp4.py
```

Script sẽ hỏi:
1. Path đến file MP3
2. Path đến file TXT

### Cách 2: Sử dụng với output từ npr_get_text_and_mp3.py

```bash
# Bước 1: Tải transcript và audio từ NPR
python npr_get_text_and_mp3.py
# Nhập URL: https://www.npr.org/transcripts/nx-s1-5655252

# Bước 2: Tạo video từ output
python mp3_and_text_to_mp4.py
# Nhập MP3 path: 2026_01_02__00_06\audio.mp3
# Nhập TXT path: 2026_01_02__00_06\transcript.txt
```

### Cách 3: Tìm file tự động

```bash
python test_video.py
```

Script sẽ tìm folder mới nhất và hiển thị path của MP3 và TXT.

## Output

Script sẽ tạo:

```
2026_01_02__00_06/
├── audio.mp3                      # File audio gốc
├── transcript.txt                 # Transcript tiếng Anh
├── transcript_vietnamese.txt      # Bản dịch tiếng Việt
└── output_video.mp4              # Video MP4 (MỚI)
```

## Cấu trúc Video

```
┌─────────────────────────────────────────────┐
│          English Transcript    │   Bản dịch tiếng Việt   │
├─────────────────────────────────────────────┤
│                                              │
│  AILSA CHANG, HOST:           │  AILSA CHANG, người dẫn: │
│                                              │
│  Today, President Trump       │  Hôm nay, Tổng thống     │
│  announced a $12 billion      │  Trump đã công bố kế     │
│  plan to help farmers...      │  hoạch 12 tỷ đô la...    │
│                                              │
│  (Text được highlight         │  (Text được highlight    │
│   khi đang đọc)                │   khi đang đọc)          │
│                                              │
└─────────────────────────────────────────────┘
```

## Ví dụ sử dụng

### Ví dụ 1: Workflow đầy đủ

```bash
# 1. Tải transcript và audio từ NPR
python npr_get_text_and_mp3.py
# URL: https://www.npr.org/transcripts/nx-s1-5655252

# Output: 2026_01_02__14_30/
#   - audio.mp3
#   - transcript.txt
#   - page.html

# 2. Tạo video từ audio và transcript
python mp3_and_text_to_mp4.py
# MP3 path: 2026_01_02__14_30\audio.mp3
# TXT path: 2026_01_02__14_30\transcript.txt

# Output:
#   - transcript_vietnamese.txt
#   - output_video.mp4
```

### Ví dụ 2: Sử dụng lại path cũ

```bash
# Lần chạy đầu tiên
python mp3_and_text_to_mp4.py
MP3 path: folder1\audio.mp3
TXT path: folder1\transcript.txt

# Lần chạy thứ hai (chỉ cần Enter)
python mp3_and_text_to_mp4.py
MP3 path lần trước: folder1\audio.mp3
Nhập path đến file MP3 (hoặc Enter để dùng path lần trước): [Enter]
TXT path lần trước: folder1\transcript.txt
Nhập path đến file TXT (hoặc Enter để dùng path lần trước): [Enter]
```

## Tùy chỉnh

### Thay đổi font chữ

Mở file `mp3_and_text_to_mp4.py` và sửa:

```python
# Dòng ~220
font_en = ImageFont.truetype("arial.ttf", 32)  # Font tiếng Anh
font_vi = ImageFont.truetype("arial.ttf", 28)  # Font tiếng Việt
```

### Thay đổi kích thước chunk

```python
# Dòng ~170
chunks_en = split_text_into_chunks(text_en, chunk_size=400)
```

Tăng `chunk_size` để hiển thị nhiều text hơn trên mỗi frame.

### Thay đổi resolution video

```python
# Dòng ~220
frame = create_text_frame(chunk_en, chunk_vi, 
                         width=1920,   # HD: 1920x1080
                         height=1080)  # 4K: 3840x2160
```

## Troubleshooting

### Lỗi: "ffmpeg not found"

**Giải pháp:**
1. Cài đặt ffmpeg: https://ffmpeg.org/download.html
2. Thêm vào PATH hoặc copy vào folder dự án

### Lỗi: "deep-translator not installed"

**Giải pháp:**
```bash
pip install deep-translator
```

### Lỗi: "PIL/Pillow not found"

**Giải pháp:**
```bash
pip install Pillow
```

### Video bị lag hoặc không sync

**Nguyên nhân:** Chia chunk không đồng đều với audio

**Giải pháp:**
- Tăng số lượng chunks (giảm `chunk_size`)
- Hoặc sử dụng speech recognition để sync chính xác hơn

### Text bị cắt hoặc không hiển thị đủ

**Giải pháp:**
- Tăng `chunk_size` trong hàm `split_text_into_chunks`
- Giảm font size

## Lưu ý

- Video render có thể mất vài phút tùy thuộc vào độ dài audio
- Chất lượng dịch phụ thuộc vào Google Translate API
- Script tự động chia text thành chunks để vừa với màn hình
- Mỗi chunk sẽ hiển thị trong thời gian đều nhau

## Kế hoạch phát triển

- [ ] Sync text chính xác hơn với audio (sử dụng speech recognition)
- [ ] Thêm animation cho text
- [ ] Cho phép chọn ngôn ngữ dịch khác
- [ ] Tùy chỉnh màu sắc và theme
- [ ] Export subtitle file (SRT/VTT)

## Công nghệ sử dụng

- **moviepy**: Tạo và render video
- **deep-translator**: Dịch text
- **Pillow**: Vẽ text lên frame
- **numpy**: Xử lý array cho frame
- **ffmpeg**: Codec và render video (bên dưới moviepy)
