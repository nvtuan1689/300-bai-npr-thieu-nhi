# HƯỚNG DẪN SỬ DỤNG CHI TIẾT

## Script npr_get_text_and_mp3.py

Script này giúp bạn tải transcript (bản ghi âm văn bản) và file audio từ các bài viết NPR.

## 📋 Yêu cầu hệ thống

- Python 3.7 trở lên
- Kết nối Internet
- Thư viện: requests, beautifulsoup4, lxml

## 🚀 Cài đặt nhanh

### Bước 1: Cài đặt Python packages

```bash
pip install -r requirements.txt
```

### Bước 2: Chạy script

```bash
python npr_get_text_and_mp3.py
```

## 📖 Hướng dẫn sử dụng từng bước

### 1. Khởi động script

Mở terminal/command prompt và chạy:

```bash
python npr_get_text_and_mp3.py
```

### 2. Nhập URL

Script sẽ hỏi bạn nhập URL của bài viết NPR. Ví dụ:

```
Nhập URL của bài viết NPR (hoặc Enter để dùng URL lần trước): 
```

Bạn có thể nhập URL đầy đủ như:
- `https://www.npr.org/transcripts/nx-s1-5655252`
- `https://www.npr.org/sections/shots-health-news/2025/12/31/nx-s1-5655252/...`

**Lưu ý:** Nếu bạn đã chạy script trước đó, script sẽ hiển thị URL lần trước và bạn chỉ cần nhấn Enter để sử dụng lại.

### 3. Quá trình xử lý

Script sẽ tự động:

1. **Tạo folder mới** với tên theo format `YYYY_MM_DD__HH_MM`
   - Ví dụ: `2026_01_01__14_30`

2. **Tải trang web** 
   - Lưu vào file `page.html`

3. **Trích xuất thông tin**
   - Tìm title (tiêu đề)
   - Tìm transcript (nội dung văn bản)
   - Lưu vào file `transcript.txt`

4. **Tải audio**
   - Tìm link audio MP3
   - Download với progress bar
   - Lưu vào file `audio.mp3`

### 4. Kết quả

Sau khi hoàn thành, bạn sẽ có một folder chứa:

```
2026_01_01__14_30/
├── page.html          # Trang web gốc (để backup)
├── transcript.txt     # Title + Transcript (không có HTML)
└── audio.mp3         # File audio MP3
```

## 🎯 Ví dụ cụ thể

### Ví dụ 1: Lần chạy đầu tiên

```
======================================================================
NPR ARTICLE SCRAPER - Lấy transcript và audio từ NPR
======================================================================

Nhập URL của bài viết NPR (hoặc Enter để dùng URL lần trước): https://www.npr.org/transcripts/nx-s1-5655252
✅ Đã tạo folder: 2026_01_01__14_30

📥 Đang tải trang web từ: https://www.npr.org/transcripts/nx-s1-5655252
✅ Đã lưu trang web: 2026_01_01__14_30\page.html

📝 Đang trích xuất title và transcript...
✅ Title: Farmers are about to pay a lot more for health insurance
✅ Transcript: 5234 ký tự

💾 Đang lưu transcript...
✅ Đã lưu transcript: 2026_01_01__14_30\transcript.txt

🎵 Đang tìm và tải audio...
🔗 Audio URL: https://ondemand.npr.org/...
⏳ Đang tải: 100.0%
✅ Đã lưu audio: 2026_01_01__14_30\audio.mp3 (3.58 MB)

======================================================================
✅ HOÀN THÀNH!
📁 Tất cả file đã được lưu vào: 2026_01_01__14_30
======================================================================
```

### Ví dụ 2: Lần chạy tiếp theo (sử dụng URL đã lưu)

```
======================================================================
NPR ARTICLE SCRAPER - Lấy transcript và audio từ NPR
======================================================================

URL lần trước: https://www.npr.org/transcripts/nx-s1-5655252
Nhập URL của bài viết NPR (hoặc Enter để dùng URL lần trước): 
Sử dụng URL: https://www.npr.org/transcripts/nx-s1-5655252
✅ Đã tạo folder: 2026_01_01__14_35
...
```

## ⚙️ Tính năng đặc biệt

### 1. Ghi nhớ URL

Script tự động lưu URL bạn đã nhập vào chính file script. Lần sau chạy, bạn chỉ cần nhấn Enter để sử dụng lại URL cũ.

### 2. Progress bar cho download audio

Khi tải audio, script hiển thị tiến độ:
```
⏳ Đang tải: 45.2%
```

### 3. Xử lý lỗi thông minh

- Nếu không tìm thấy audio: Script vẫn lưu transcript
- Nếu không tìm thấy transcript: Script thông báo nhưng vẫn tiếp tục
- Nếu URL không hợp lệ: Script dừng ngay và báo lỗi rõ ràng

## 🔧 Troubleshooting

### Lỗi: "Module not found"

**Giải pháp:**
```bash
pip install -r requirements.txt
```

### Lỗi: "Connection timeout"

**Nguyên nhân:** Kết nối Internet chậm hoặc NPR đang bảo trì

**Giải pháp:** 
- Kiểm tra kết nối Internet
- Thử lại sau vài phút

### Lỗi: "Không tìm thấy transcript"

**Nguyên nhân:** Trang web có cấu trúc khác với mẫu

**Giải pháp:**
- Kiểm tra xem URL có đúng không
- Thử với URL khác từ NPR
- Xem file `page.html` để kiểm tra nội dung

### Lỗi: "Không tìm thấy audio"

**Nguyên nhân:** Một số bài viết NPR không có audio

**Giải pháp:**
- Script vẫn sẽ lưu transcript
- Bạn vẫn có thể sử dụng transcript để làm việc khác

## 💡 Tips & Tricks

### Tip 1: Tìm URL transcript NPR

Từ một bài viết NPR bất kỳ, tìm nút "Transcript" và click vào. URL sẽ có dạng:
```
https://www.npr.org/transcripts/[story-id]
```

### Tip 2: Batch processing (xử lý nhiều bài)

Bạn có thể tạo một file `urls.txt` chứa danh sách URL và viết script Python nhỏ để xử lý:

```python
import subprocess

with open('urls.txt', 'r') as f:
    urls = f.readlines()

for url in urls:
    url = url.strip()
    # Simulate input
    subprocess.run(['python', 'npr_get_text_and_mp3.py'], 
                   input=url, text=True)
```

### Tip 3: Tùy chỉnh folder output

Nếu bạn muốn tự đặt tên folder, sửa dòng trong script:

```python
folder_name = now.strftime("%Y_%m_%d__%H_%M")
```

Thành:

```python
folder_name = input("Nhập tên folder: ")
```

## 📞 Hỗ trợ

Nếu gặp vấn đề, hãy:
1. Kiểm tra lại requirements.txt đã cài đủ chưa
2. Xem file `page.html` để debug
3. Chạy `demo_test.py` để test từng chức năng

## 🎓 Học thêm

Script này sử dụng:
- **requests**: HTTP library để tải web
- **BeautifulSoup**: HTML parser để trích xuất nội dung
- **re**: Regular expressions để tìm audio URL

Bạn có thể học thêm về web scraping tại:
- https://docs.python-requests.org/
- https://www.crummy.com/software/BeautifulSoup/
