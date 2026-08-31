import subprocess

ffmpeg_path = r"C:\Users\anant\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg.Essentials_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1.1-essentials_build\bin\ffmpeg.exe"

def test_yt_dlp():
    url = "https://www.youtube.com/watch?v=aqz-KE-bpKQ"
    command = [
        "python",
        "-m",
        "yt_dlp",
        "--js-runtimes", "node",
        "--ffmpeg-location", ffmpeg_path,
        "-f", "bestvideo[protocol^=m3u8]+bestaudio[protocol^=m3u8]/bestvideo[ext=mp4]+bestaudio[ext=m4a]/best",
        "--download-sections", "*00:01:00-00:01:10",
        "--force-keyframes-at-cuts",
        "-o", "test_clip_audio_fix.mp4",
        url
    ]
    print(subprocess.list2cmdline(command))
    subprocess.run(command)

test_yt_dlp()
