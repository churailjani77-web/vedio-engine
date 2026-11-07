from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import urllib.request
import urllib.parse
import json
import yt_dlp

app = FastAPI(title="Namaz Ka Sakoon Video Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"status": "online", "message": "Namaz Ka Sakoon Video Engine 100% Active 🚀"}

# 1. TIKTOK ENGINE (Unwatermarked + Safe Title)
def get_tiktok(url: str):
    api_url = "https://www.tikwm.com/api/?url=" + urllib.parse.quote(url)
    req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=10) as response:
        result = json.loads(response.read().decode('utf-8'))
        data = result.get("data", {})
        play_url = data.get("play") or data.get("wmplay")
        if play_url:
            title = data.get("title")
            if not title or not str(title).strip():
                title = "TikTok Video"

            return {
                "success": True,
                "title": title,
                "thumbnail": data.get("cover"),
                "video_url": play_url,
                "platform": "TikTok"
            }
    return None

# 🚀 YOUTUBE 100% BOT-BYPASS ENGINE:
def get_youtube(url: str):
    # Video ID nikalna
    video_id = None
    if "shorts/" in url:
        video_id = url.split("shorts/")[1].split("?")[0].split("/")[0]
    elif "watch?v=" in url:
        video_id = url.split("watch?v=")[1].split("&")[0]
    elif "youtu.be/" in url:
        video_id = url.split("youtu.be/")[1].split("?")[0]

    if not video_id:
        return None

    # Invidious / Piped Gateway (No Bot Block!)
    gateways = [
        f"https://api.invidious.io/api/v1/videos/{video_id}",
        f"https://pipedapi.kavin.rocks/streams/{video_id}"
    ]

    for api_url in gateways:
        try:
            req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=6) as response:
                data = json.loads(response.read().decode('utf-8'))
                
                # Direct MP4 stream dhoondna
                streams = data.get("formatStreams") or data.get("videoStreams") or []
                for s in streams:
                    if s.get("url") and ("mp4" in s.get("container", "").lower() or "mp4" in s.get("mimeType", "").lower()):
                        return {
                            "success": True,
                            "title": data.get("title", "YouTube Video"),
                            "thumbnail": f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg",
                            "video_url": s.get("url"),
                            "platform": "YouTube"
                        }
        except Exception:
            continue
    return None

@app.get("/download")
def download_api(url: str = Query(..., description="Target Video URL")):
    if not url:
        raise HTTPException(status_code=400, detail="URL missing!")

    url = url.strip()

    # TikTok Fast Path:
    if "tiktok.com" in url or "vt.tiktok" in url:
        try:
            res = get_tiktok(url)
            if res:
                return res
        except Exception:
            pass
# Agar YouTube ho to Bypass Engine chalao:
    if "youtube.com" in url or "youtu.be" in url:
        yt_res = get_youtube(url)
        if yt_res:
            return yt_res
    # Universal Path:
    try:
        return get_universal(url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
