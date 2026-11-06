import re, shutil, tempfile, time, uuid
from pathlib import Path
from urllib.parse import urlparse
import yt_dlp
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, HttpUrl
from starlette.background import BackgroundTask

BASE = Path(__file__).resolve().parent
TMP = Path(tempfile.gettempdir()) / "tikdown"
TMP.mkdir(parents=True, exist_ok=True)
app = FastAPI(title="TikDown", docs_url=None, redoc_url=None)
app.mount("/static", StaticFiles(directory=BASE / "static"), name="static")
ALLOWED = {"tiktok.com", "www.tiktok.com", "m.tiktok.com", "vm.tiktok.com", "vt.tiktok.com"}
hits = []
class Request(BaseModel):
    url: HttpUrl

def cleanup(path): shutil.rmtree(path, ignore_errors=True)

@app.get("/health")
def health(): return {"status": "ok", "app": "TikDown"}

@app.get("/")
def home(): return FileResponse(BASE / "static" / "index.html")

@app.post("/api/download")
def download(req: Request):
    url = str(req.url)
    host = (urlparse(url).hostname or "").lower()
    if not any(host == d or host.endswith("." + d) for d in ALLOWED):
        raise HTTPException(400, "Please enter a valid TikTok video URL.")
    now = time.time()
    hits[:] = [t for t in hits if now - t < 60]
    if len(hits) >= 5:
        raise HTTPException(429, "Too many requests. Please wait a minute.")
    hits.append(now)
    folder = TMP / uuid.uuid4().hex
    folder.mkdir(parents=True)
    opts = {"outtmpl": str(folder / "%(id)s.%(ext)s"), "format": "best[ext=mp4]/best",
            "noplaylist": True, "quiet": True, "no_warnings": True,
            "restrictfilenames": True, "merge_output_format": "mp4",
            "socket_timeout": 25, "retries": 2, "max_filesize": 150*1024*1024}
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            prepared = Path(ydl.prepare_filename(info))
        choices = [prepared, prepared.with_suffix(".mp4")]
        output = next((p for p in choices if p.exists()), None)
        if output is None:
            output = next(iter(folder.glob("*")), None)
        if output is None or not output.exists(): raise RuntimeError("Missing download")
        title = re.sub(r"[^A-Za-z0-9._ -]", "", info.get("title") or "TikDown-video").strip()[:70]
        return FileResponse(output, media_type="video/mp4" if output.suffix.lower()==".mp4" else "application/octet-stream",
                            filename=(title or "TikDown-video")+output.suffix,
                            background=BackgroundTask(cleanup, str(folder)))
    except Exception as exc:
        cleanup(str(folder))
        raise HTTPException(422, "TikTok could not provide this video. It may be private, unavailable, or temporarily unsupported.") from exc
