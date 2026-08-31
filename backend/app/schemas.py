from pydantic import BaseModel, constr, validator
import re

YOUTUBE_REGEX = re.compile(r"(https?://)?(www\.)?(youtube\.com|youtu\.be)/")


class ClipRequest(BaseModel):
    url: constr(strip_whitespace=True, min_length=5)
    start: constr(strip_whitespace=True)
    end: constr(strip_whitespace=True)

    @validator('url')
    def validate_url(cls, v):
        if not YOUTUBE_REGEX.search(v):
            raise ValueError('Invalid YouTube URL')
        return v

    @validator('start', 'end')
    def validate_timestamp(cls, v):
        # Accept SS, MM:SS or HH:MM:SS
        pattern = re.compile(r'^\d{1,2}(:\d{1,2}){0,2}$')
        if not pattern.match(v):
            raise ValueError('Invalid timestamp format. Use SS, MM:SS or HH:MM:SS')
        return v
