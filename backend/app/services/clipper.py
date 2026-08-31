import logging
from pathlib import Path
from typing import Tuple

logger = logging.getLogger(__name__)


def parse_timestamp(ts: str) -> int:
    """Parse a timestamp string (SS, MM:SS, HH:MM:SS) into total seconds."""
    parts = [int(p) for p in ts.split(":")]
    seconds = 0
    for p in parts:
        seconds = seconds * 60 + p
    return seconds


def build_yt_dlp_command(url: str, start: str, end: str, output_path: Path) -> list[str]:
    """Return a list of arguments to call yt-dlp without shell=True.

    Note: This is a helper to construct the command; execution is handled elsewhere.
    """
    section = f"*{start}-{end}"
    cmd = [
        "yt-dlp",
        "--rm-cache-dir",
        "--no-warnings",
        "-f",
        "bestvideo+bestaudio/best",
        "--download-sections",
        section,
        "-o",
        str(output_path),
    ]
    return cmd
