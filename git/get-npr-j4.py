import os, json, html, requests
from moviepy.editor import *
from whisper_timestamped import load_model, transcribe
from googletrans import Translator
from PIL import Image
from io import BytesIO

def download_background(title, bg_file="background.jpg"):
    """Dùng Unsplash random image theo title"""
    query = title.replace(" ", "+")
    url = f"https://source.unsplash.com/1280x720/?{query}"
    r = requests.get(url)
    if r.status_code == 200:
        with open(bg_file, "wb") as f:
            f.write(r.content)
        print(f"Đã tải background cho: {title}")
    return bg_file

def generate_subs(audio_file, model_size="small", cache_file="subs.json"):
    if os.path.exists(cache_file):
        with open(cache_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data["segments"], data["duration"]

    model = load_model(model_size)
    result = transcribe(model, audio_file, language="en")

    segments = []
    translator = Translator()
    for seg in result["segments"]:
        en_text = seg["text"].strip()
        if not en_text:
            continue
        vi_text = translator.translate(en_text, src="en", dest="vi").text
        segments.append({
            "start": seg["start"],
            "end": seg["end"],
            "en": en_text,
            "vi": vi_text
        })

    duration = AudioFileClip(audio_file).duration

    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump({"segments": segments, "duration": duration}, f, ensure_ascii=False, indent=2)

    return segments, duration

def make_video(audio_file, subs, duration, title, output_file="npr_audio.mp4"):
    # Dùng ảnh background
    bg_file = download_background(title)
    bg_clip = ImageClip(bg_file).set_duration(duration).resize((1280, 720))

    audio = AudioFileClip(audio_file)
    bg_clip = bg_clip.set_audio(audio)

    def make_subtitle_frame(t):
        current = None
        for seg in subs:
            if seg["start"] <= t <= seg["end"]:
                current = seg
                break

        idx = subs.index(current) if current else -1
        prev_line = subs[idx-1] if idx > 0 else None
        next_line = subs[idx+1] if idx >= 0 and idx < len(subs)-1 else None

        lines = []
        if prev_line:
            lines.append(f"<font color='gray'>{html.escape(prev_line['en'])}<br/>{html.escape(prev_line['vi'])}</font>")
        if current:
            lines.append(f"<font color='yellow'>{html.escape(current['en'])}<br/>{html.escape(current['vi'])}</font>")
        if next_line:
            lines.append(f"<font color='gray'>{html.escape(next_line['en'])}<br/>{html.escape(next_line['vi'])}</font>")

        text = "<br/><br/>".join(lines) if lines else " "

        txt_clip = TextClip(
            txt=text,
            font="Arial-Bold",
            fontsize=60,   # chữ to hơn
            color="white",
            method="caption",
            size=(1100, None)
        )
        return txt_clip.set_position(("center", "center")).get_frame(0)

    subtitle_clip = VideoClip(make_subtitle_frame, duration=duration)

    final = CompositeVideoClip([bg_clip, subtitle_clip])
    final.write_videofile(output_file, fps=24)

if __name__ == "__main__":
    audio_file = "npr_audio.mp3"
    title = "Children's Science Story"  # TODO: lấy tự động từ transcript
    subs, duration = generate_subs(audio_file, model_size="small")
    make_video(audio_file, subs, duration, title, "npr_audio.mp4")

    if os.path.exists("subs.json"):
        os.remove("subs.json")
        print("Đã xóa cache subs.json")
