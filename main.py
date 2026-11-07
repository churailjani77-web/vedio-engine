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

# 🎯 ENGINE 2 (TikTok & Instagram Backup Gateway):
def engine_tiklydown(url: str):
    api_url = "https://api.tiklydown.eu.org/api/download?url=" + urllib.parse.quote(url)
    req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=8) as response:
        data = json.loads(response.read().decode('utf-8'))
        
        # TikTok ya Instagram video link nikalna:
        video_url = data.get("video", {}).get("noWatermark") or data.get("url") or data.get("video", {}).get("watermark")
        if video_url:
            title = data.get("title")
            return {
                "success": True,
                "title": title if (title and str(title).strip()) else "Social Video",
                "thumbnail": data.get("video", {}).get("cover") or data.get("thumbnail"),
                "video_url": video_url,
                "platform": "Backup Engine 2"
            }
    return None

# 🎯 ENGINE 3 (Universal yt-dlp: Facebook, Snapchat, Insta, Ultimate Backup):
def engine_universal(url: str):
    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        video_url = info.get('url')
        if not video_url and 'entries' in info and len(info['entries']) > 0:
            video_url = info['entries'][0].get('url')

        if not video_url:
            raise Exception("Stream link nahi mil saka.")

        title = info.get('title')
        return {
            "success": True,
            "title": title if (title and str(title).strip()) else "Downloaded Video",
            "thumbnail": info.get('thumbnail'),
            "video_url": video_url,
            "platform": info.get('extractor_key', 'Universal Engine 3')
        }

# 🚀 MASTER ROUTER (TikTok, Instagram, Facebook, Snapchat):
@app.get("/download")
def download_api(url: str = Query(..., description="Target Video URL")):
    if not url:
        raise HTTPException(status_code=400, detail="URL missing!")

    url = url.strip()

    # 1. TIKTOK KE 3 ENGINES:
    if "tiktok.com" in url or "vt.tiktok" in url:
        # Pehla Asali Working Engine:
        try:
            res1 = get_tiktok(url)
            if res1: return res1
        except Exception:
            pass

        # Doosra Backup Engine:
        try:
            res2 = engine_tiklydown(url)
            if res2: return res2
        except Exception:
            pass

    # 2. INSTAGRAM KE 2 ENGINES:
    if "instagram.com" in url:
        try:
            res_insta = engine_tiklydown(url)
            if res_insta: return res_insta
        except Exception:
            pass

    # 3. UNIVERSAL (Facebook, Snapchat, aur sab ka Aakhri Backup Engine):
    try:
        return engine_universal(url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
