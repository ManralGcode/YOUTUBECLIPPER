import subprocess
import json

ffmpeg_path = r"C:\Users\anant\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg.Essentials_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1.1-essentials_build\bin\ffmpeg.exe"

def test():
    url = "https://www.youtube.com/watch?v=aqz-KE-bpKQ"
    
    # 1. Get URL
    cmd_url = [
        "python", "-m", "yt_dlp", "--js-runtimes", "node", "--dump-json", "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best", url
    ]
    res = subprocess.run(cmd_url, capture_output=True, text=True)
    info = json.loads(res.stdout)
    
    url_v = info.get("requested_formats", [info])[0].get("url")
    url_a = info.get("requested_formats", [info])[-1].get("url")
    
    print("Got URLs")
    
    # 2. Run ffmpeg
    if url_v == url_a:
        cmd_ffmpeg = [
            ffmpeg_path, "-y",
            "-ss", "00:01:00", "-to", "00:01:10",
            "-i", url_v,
            "-c", "copy",
            "test_clip2.mp4"
        ]
    else:
        cmd_ffmpeg = [
            ffmpeg_path, "-y",
            "-ss", "00:01:00", "-to", "00:01:10", "-i", url_v,
            "-ss", "00:01:00", "-to", "00:01:10", "-i", url_a,
            "-c", "copy",
            "test_clip2.mp4"
        ]
    
    print(subprocess.list2cmdline(cmd_ffmpeg))
    subprocess.run(cmd_ffmpeg)

test()
