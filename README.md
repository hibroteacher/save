# TikDown

Ad-free TikTok downloader starter project. FastAPI serves the responsive frontend and `/api/download` backend from the same app.

## Deploy from GitHub (Render)

**GitHub stores the source code. GitHub Pages cannot run this Python backend.** To make downloading work, connect this repository to a Python-capable host.

1. Create a GitHub repository named `tikdown`.
2. Upload/push every file in this project to the repository root.
3. In Render, choose **New → Blueprint** and connect the GitHub repository.
4. Render detects `render.yaml`; review and create the `tikdown` web service.
5. Open the Render URL. It serves both the website and download API.

The blueprint requests a free plan where offered. Free services may sleep when idle and have limits; check current hosting terms and pricing.

## Run locally

Requires Python 3.10+.

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 8000
```

Open `http://localhost:8000`; health check: `/health`.

## Hosting requirements

Python ASGI or Docker support is required; PHP-only shared hosting will not run this as-is. Use the included Dockerfile if needed. FFmpeg may be required to merge separate audio/video streams.

## Limitations and production notes

- No ad scripts, analytics, tracking pixels, or accounts are included.
- yt-dlp retrieves the best format available to it. Watermark-free output, 4K, and all resolutions cannot be guaranteed; they depend on TikTok's source and extractor support.
- Private, deleted, region/age-restricted videos may fail. This app does not bypass private-account restrictions.
- TikTok may change delivery methods; keep yt-dlp updated.
- The included basic rate limiter is process-local and shared, not per-user. Before public launch, add proper per-IP rate limiting, download concurrency/storage quotas, proxy timeouts, and disk monitoring.
- Use only content you own or have permission to download; respect copyright and TikTok's terms.
