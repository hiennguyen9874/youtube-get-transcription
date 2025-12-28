from fastapi import FastAPI, HTTPException
import yt_dlp
import requests

app = FastAPI()


def parse_youtube_json3(data):
    """
    Hàm phụ trợ để trích xuất text từ định dạng JSON3 của Youtube
    (loại chứa wireMagic, events, segs...)
    """
    text_parts = []
    events = data.get("events", [])

    for event in events:
        # Mỗi event có thể chứa nhiều segments (segs)
        segs = event.get("segs", [])
        for seg in segs:
            # Lấy nội dung text trong trường 'utf8'
            content = seg.get("utf8", "")
            if content and content != "\n":
                text_parts.append(content)

    # Nối lại thành 1 chuỗi, loại bỏ khoảng trắng thừa
    full_text = "".join(text_parts).replace("\n", " ").strip()
    return full_text


@app.get("/transcribe")
def get_transcription(url: str, lang: str = "en"):
    ydl_opts = {
        "skip_download": True,
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "writesubtitles": True,
        "writeautomaticsub": True,
        "subtitleslangs": ["en.*", "vi.*"],
        # THAY ĐỔI Ở ĐÂY:
        # Thay vì dùng Postprocessor (FFmpeg), hãy dùng cái này để yêu cầu format từ server
        "subtitlesformat": "srt/vtt/best",
        # Thêm cái này để giảm thời gian chờ kết nối
        "socket_timeout": 10,  # Timeout ngắn để bỏ qua các kết nối lỗi nhanh hơn
        "retries": 2,  # Thử lại ít lần thôi để tiết kiệm thời gian
        # Quan trọng nếu chạy trong Docker: Tránh ghi file tạm thừa thãi
        "source_address": "0.0.0.0",  # Ép sử dụng IPv4,
        "nocheckcertificate": True,  # Bỏ qua kiểm tra SSL (giúp nhanh hơn một chút trong Docker)
        "geo_bypass": True,  # Vượt rào cản địa lý nếu có,
        "outtmpl": "%(id)s.%(ext)s",  # Đặt tên file ngắn gọn (ID video)
        "overwrites": True,  # Ghi đè file cũ để tránh xung đột file trong Docker,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # 1. Lấy thông tin video
            info = ydl.extract_info(url, download=False)

            video_title = info.get("title", "Unknown Title")
            video_url = info.get("webpage_url", url)

            # 2. Tìm phụ đề (ưu tiên auto-generated)
            captions = info.get("automatic_captions") or info.get("subtitles")

            if not captions:
                return {"error": "Video không có phụ đề"}

            selected_lang = lang if lang in captions else next(iter(captions))

            # 3. Tìm link tải định dạng 'json3' để dễ parse
            # Youtube cung cấp nhiều định dạng (vtt, srv1, json3...), ta cần json3
            sub_list = captions[selected_lang]
            json_url = None

            for sub in sub_list:
                if sub.get("ext") == "json3":
                    json_url = sub.get("url")
                    break

            # Nếu không tìm thấy json3, lấy cái đầu tiên (fallback)
            if not json_url:
                json_url = sub_list[0]["url"]

            # 4. Tải và xử lý nội dung
            response = requests.get(json_url)

            print(response)

            raw_data = response.json()

            # Gọi hàm parse để merge text
            transcript_text = parse_youtube_json3(raw_data)

            # 5. Trả về kết quả đúng format yêu cầu
            return {
                "title": video_title,
                "video_url": video_url,
                "transcription": transcript_text,
            }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
