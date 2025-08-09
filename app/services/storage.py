import os
import io
import shutil
from pathlib import Path
from typing import Optional, BinaryIO
import logging

logger = logging.getLogger(__name__)

UPLOAD_DIR = Path("/app/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

class StorageService:
    """Almacenamiento local basado en filesystem (Railway Volumes)."""

    def __init__(self) -> None:
        self.base_path = UPLOAD_DIR

    def upload_file(self, file_data: BinaryIO, filename: str, content_type: str = "application/octet-stream") -> str:
        file_path = self.base_path / filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file_data, buffer)
        logger.info(f"Archivo guardado localmente: {file_path}")
        return str(file_path)

    def download_file(self, object_name: str) -> Optional[BinaryIO]:
        file_path = Path(object_name)
        if not file_path.is_absolute():
            file_path = self.base_path / object_name
        if not file_path.exists():
            return None
        return open(file_path, "rb")

    def delete_file(self, object_name: str) -> bool:
        file_path = Path(object_name)
        if not file_path.is_absolute():
            file_path = self.base_path / object_name
        try:
            os.remove(file_path)
            logger.info(f"Archivo eliminado: {file_path}")
            return True
        except Exception:
            return False

# Instancia global
storage_service = StorageService()
