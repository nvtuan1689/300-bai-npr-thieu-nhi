import os
import re
import requests
from bs4 import BeautifulSoup


def get_npr_transcript(page_url: str,
                       mp3_filename: str,
                       dest_folder: str = ".",
                       timeout: int = 15,
                       verbose: bool = True) -> str | None:
    """
    Lấy transcript tiếng Anh từ NPR và lưu vào file .txt
    Tên file .txt sẽ trùng tên file mp3 (nhưng đuôi .txt)

    Args:
        page_url: URL transcript NPR
        mp3_filename: tên file mp3 đã tải ở Job 1
        dest_folder: thư mục lưu file
        timeout: timeout request
        verbose: in tiến trình

    Returns:
        Đường dẫn file .txt đã lưu, hoặc None nếu không tìm thấy transcript
    """
    resp = requests.get(page_url, timeout=timeout)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")

    # --- Lấy tiêu đề ---
    title_tag = soup.find("h1")
    title = title_tag.get_text(strip=True) if title_tag else "Untitled"

    # --- Lấy ngày tháng (thường nằm trong <time> hoặc <span>) ---
    date_text = ""
    time_tag = soup.find("time")
    if time_tag:
        date_text = time_tag.get_text(strip=True)
    else:
        # fallback: tìm meta
        meta_date = soup.find("meta", {"name": "date"})
        if meta_date and meta_date.get("content"):
            date_text = meta_date["content"]

    # --- Lấy nội dung transcript ---
    transcript_div = soup.find("div", {"id": "transcript"})
    if not transcript_div:
        transcript_div = soup.find("article")

    if not transcript_div:
        if verbose:
            print("Không tìm thấy transcript trong HTML.")
        return None

    paragraphs = [p.get_text(strip=True) for p in transcript_div.find_all("p")]
    text = "\n".join(paragraphs)

    # --- Cắt đến hết phần Copyright ---
    # Regex: Copyright © <4 số> NPR...
    match = re.search(r"Copyright © \\d{4} NPR\\. All rights reserved.*", text, flags=re.DOTALL)
    if match:
        end_idx = match.end()
        text = text[:end_idx]

    # --- Gom full nội dung ---
    full_text = f"{title}\n{date_text}\n\n{text}\n"

    # --- Xuất file .txt ---
    base, _ = os.path.splitext(mp3_filename)
    txt_filename = f"{base}.txt"
    os.makedirs(dest_folder, exist_ok=True)
    dest_path = os.path.join(dest_folder, txt_filename)

    with open(dest_path, "w", encoding="utf-8") as f:
        f.write(full_text)

    if verbose:
        print("Đã lưu transcript:", dest_path)

    return dest_path


# --- Ví dụ sử dụng ---
if __name__ == "__main__":
    example = "https://www.npr.org/transcripts/nx-s1-5527020"
    mp3_file = "npr_audio.mp3"   # giả sử Job 1 đã tải xong
    txt_path = get_npr_transcript(example, mp3_file)
    print("Kết quả transcript:", txt_path)
