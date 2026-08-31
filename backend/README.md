# YouTube Clipper - Backend

This folder contains the FastAPI backend for the YouTube Timestamp Clipper.

Prerequisites

- Python 3.12
- FFmpeg installed and available on PATH
- yt-dlp installed (`pip install yt-dlp`)

Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Run (development)

```powershell
uvicorn app.main:app --reload --port 8000
```

What we built so far

- Minimal FastAPI app skeleton with `GET /` health endpoint
- Request schema and clipper service placeholders

Next steps

- Implement `POST /clip` to run `yt-dlp` + `ffmpeg` safely and stream MP4 output
