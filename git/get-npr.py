import os
import re
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


def download_npr_mp3(page_url: str,
                     dest_folder: str = ".",
                     filename: str | None = None,
                     timeout: int = 15,
                     session: requests.Session | None = None,
                     verbose: bool = True) -> str | None:
    """
    Tải file .mp3 từ một trang transcript NPR (nếu tìm được).
    Trả về đường dẫn file đã lưu, hoặc None nếu không tìm thấy mp3 trong HTML.

    Args:
        page_url: URL trang transcript (ví dụ: https://www.npr.org/transcripts/...)
        dest_folder: thư mục lưu file
        filename: tên file muốn lưu (mặc định lấy từ URL mp3)
        timeout: timeout request (giây)
        session: optional requests.Session() để tái sử dụng connection
        verbose: in tiến trình

    Trả về:
        path tới file mp3 (str) nếu download thành công, hoặc None nếu không tìm thấy link mp3.
    """
    if session is None:
        session = requests.Session()
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/115.0 Safari/537.36"
        })

    resp = session.get(page_url, timeout=timeout)
    resp.raise_for_status()
    text = resp.text
    soup = BeautifulSoup(text, "lxml")

    candidates = []

    # 1) thẻ <audio> hoặc <source>
    for audio in soup.find_all("audio"):
        src = audio.get("src")
        if src:
            candidates.append(urljoin(page_url, src))
        for source in audio.find_all("source"):
            s = source.get("src")
            if s:
                candidates.append(urljoin(page_url, s))

    # 2) thẻ <a href="...mp3">
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if ".mp3" in href.lower():
            candidates.append(urljoin(page_url, href))

    # 3) JSON-LD (application/ld+json) có thể chứa contentUrl hoặc audio
    for script in soup.find_all("script", {"type": "application/ld+json"}):
        try:
            import json
            data = json.loads(script.string or "{}")

            def extract(obj):
                if isinstance(obj, dict):
                    for k, v in obj.items():
                        if isinstance(v, str) and ".mp3" in v.lower():
                            candidates.append(urljoin(page_url, v))
                        else:
                            extract(v)
                elif isinstance(obj, list):
                    for it in obj:
                        extract(it)

            extract(data)
        except Exception:
            pass

    # 4) regex trên HTML (bắt tất cả https://...*.mp3)
    found = re.findall(r"https?://[^\"'\s<>]+?\.mp3(?:\?[^\"'\s<>]+)?", text, flags=re.IGNORECASE)
    candidates.extend(found)

    # dedupe & absolute URLs
    seen = []
    for c in candidates:
        if not c:
            continue
        abs_url = urljoin(page_url, c)
        if abs_url not in seen:
            seen.append(abs_url)
    candidates = seen

    if not candidates:
        if verbose:
            print("Không tìm thấy link .mp3 trong HTML. Có khả năng audio được load bằng JavaScript.")
            print("Nếu vậy, cân nhắc dùng Selenium/Playwright hoặc cung cấp URL mp3 trực tiếp.")
        return None

    # ưu tiên các link có 'npr' hoặc 'audio'
    def score(u: str) -> int:
        s = 0
        lu = u.lower()
        if "npr" in lu:
            s += 2
        if "audio" in lu or "media" in lu:
            s += 1
        if lu.endswith(".mp3") or ".mp3?" in lu:
            s += 1
        return s

    candidates.sort(key=score, reverse=True)
    audio_url = candidates[0]

    # chuẩn tên file
    if filename is None:
        parsed = urlparse(audio_url)
        base = os.path.basename(parsed.path)
        filename = base or "npr_audio.mp3"

    os.makedirs(dest_folder, exist_ok=True)
    dest_path = os.path.join(dest_folder, filename)

    # download stream
    r = session.get(audio_url, stream=True, timeout=timeout)
    r.raise_for_status()
    total = int(r.headers.get("content-length", 0))

    with open(dest_path, "wb") as fw:
        downloaded = 0
        for chunk in r.iter_content(chunk_size=8192):
            if not chunk:
                continue
            fw.write(chunk)
            downloaded += len(chunk)
            if verbose and total:
                percent = downloaded * 100 // total
                print(f"\rDownloading {filename}: {downloaded}/{total} bytes ({percent}%)", end="")

    if verbose:
        if total:
            print()
        print("Lưu thành:", dest_path)

    return dest_path


# --- Ví dụ sử dụng ---
if __name__ == "__main__":
    example = "https://www.npr.org/transcripts/nx-s1-5527020"
    print("Thử với:", example)
    path = download_npr_mp3(example)
    print("Kết quả:", path)
