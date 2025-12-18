import os
from pathlib import Path
from typing import Optional

from fastapi import UploadFile

from app.core.config import get_settings

settings = get_settings()


async def save_upload(file: UploadFile) -> str:
    ext = Path(file.filename or "upload").suffix
    filename = f"product_{os.urandom(8).hex()}{ext}"
    media_dir = settings.media_root_path
    media_dir.mkdir(parents=True, exist_ok=True)
    destination = media_dir / filename

    with destination.open("wb") as buffer:
        while content := await file.read(1024 * 1024):
            buffer.write(content)
    await file.close()
    return str(destination)
