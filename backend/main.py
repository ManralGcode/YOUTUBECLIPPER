import os
import re
import sys
import uuid
import json
import subprocess
import tempfile
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, field_validator

# Setup paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMP_DIR = os.path.join(BASE_DIR, "temp")
DOWNLOADS_DIR = os.path.join(BASE_DIR, "downloads")

# Ensure directories exist
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(DOWNLOADS_DIR, exist_ok=True)

app = FastAPI(title="YouTube Clipper API")

# Allow CORS for the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ClipRequest(BaseModel):
    url: str
    start: str
    end: str

    @field_validator('url', mode='before')
    @classmethod
    def validate_youtube_url(cls, v: str) -> str:
        v = v.strip()
        # Regex to validate YouTube URL format
        pattern = r'^(https?\:\/\/)?(www\.youtube\.com|youtu\.be)\/.+$'
        if not re.match(pattern, v):
            raise ValueError('Invalid YouTube URL')
        return v

    @field_validator('start', 'end', mode='before')
    @classmethod
    def validate_timestamp(cls, v: str) -> str:
        v = v.strip()
        # Format HH:MM:SS or MM:SS
        pattern = r'^(\d{1,2}:)?([0-5]\d):([0-5]\d)$'
        if not re.match(pattern, v):
            raise ValueError('Timestamp must be in HH:MM:SS or MM:SS format')
        return v

def cleanup_file(filepath: str):
    """Deletes a file if it exists."""
    if os.path.exists(filepath):
        try:
            os.remove(filepath)
            print(f"Cleaned up file: {filepath}")
        except Exception as e:
            print(f"Failed to delete {filepath}: {e}")

@app.get("/")
async def root():
    return {"status": "online"}

class URLRequest(BaseModel):
    url: str

    @field_validator('url', mode='before')
    @classmethod
    def validate_youtube_url(cls, v: str) -> str:
        v = v.strip()
        pattern = r'^(https?\:\/\/)?(www\.youtube\.com|youtu\.be)\/.+$'
        if not re.match(pattern, v):
            raise ValueError('Invalid YouTube URL')
        return v

@app.post("/metadata")
def get_metadata(request: URLRequest):
    try:
        command = [
            sys.executable,
            "-m",
            "yt_dlp",
            "--impersonate", "chrome",
            "--dump-json",
            "--no-playlist",
            request.url
        ]
        with tempfile.TemporaryFile(mode='w+', encoding='utf-8') as temp_out, tempfile.TemporaryFile(mode='w+', encoding='utf-8') as temp_err:
            process = subprocess.run(command, stdout=temp_out, stderr=temp_err, stdin=subprocess.DEVNULL, text=True)
            temp_out.seek(0)
            stdout_data = temp_out.read()
            temp_err.seek(0)
            stderr_data = temp_err.read()
            
        if process.returncode != 0:
            raise HTTPException(status_code=400, detail=f"Could not fetch metadata. Ensure it is a valid video. Error: {stderr_data}")
        
        info = json.loads(stdout_data)
        return {
            "title": info.get("title"),
            "thumbnail": info.get("thumbnail"),
            "duration_string": info.get("duration_string"),
            "uploader": info.get("uploader")
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.post("/clip")
def create_clip(request: ClipRequest, background_tasks: BackgroundTasks):
    try:
        # Generate a unique filename for the temporary file
        filename = f"{uuid.uuid4()}.mp4"
        output_path = os.path.join(TEMP_DIR, filename)

        # Format the section string for yt-dlp
        # Syntax requires a '*' before the timestamps (e.g., *00:10:15-00:12:40)
        section_str = f"*{request.start}-{request.end}"

        command = [
            sys.executable,
            "-m",
            "yt_dlp",
            "--impersonate", "chrome",
        ]
        
        # Use explicit path for local Windows development if it exists
        local_ffmpeg = r"C:\Users\anant\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg.Essentials_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1.1-essentials_build\bin"
        if os.path.exists(local_ffmpeg):
            command.extend(["--ffmpeg-location", local_ffmpeg])
            
        command.extend([
            "-f", "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            "--compat-options", "no-direct-merge",
            "--force-keyframes-at-cuts",
            "--download-sections", section_str,
            "--downloader-args", "ffmpeg:-c:v libx264 -preset ultrafast -c:a aac",
            "-o", output_path,
            request.url
        ])

        # Execute yt-dlp using subprocess
        process = subprocess.run(
            command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            text=True
        )

        # Check if the command was successful
        if process.returncode != 0:
            raise HTTPException(
                status_code=500, 
                detail="Failed to download the clip."
            )

        # Verify the file was actually created
        if not os.path.exists(output_path):
            raise HTTPException(status_code=500, detail="The clip was not generated successfully.")

        # Schedule the temporary file to be deleted AFTER the response is sent back
        background_tasks.add_task(cleanup_file, output_path)

        # Return the video file stream to the client
        return FileResponse(
            path=output_path, 
            media_type="video/mp4", 
            filename="youtube_clip.mp4"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
