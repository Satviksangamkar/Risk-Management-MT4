"""
File Utilities
Helper functions for file handling and validation
"""

import os
import uuid
from pathlib import Path
from typing import Optional, Tuple

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


def ensure_upload_directory() -> Path:
    """Ensure upload directory exists"""
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(exist_ok=True)
    return upload_dir


def generate_unique_filename(original_filename: str) -> str:
    """Generate a unique filename while preserving extension"""
    extension = Path(original_filename).suffix
    unique_id = str(uuid.uuid4())[:8]
    timestamp = str(int(os.time.time()))
    return f"{timestamp}_{unique_id}{extension}"


def save_upload_file(upload_file, destination_path: Path) -> Tuple[bool, Optional[str]]:
    """Save uploaded file to destination"""
    try:
        with open(destination_path, 'wb') as buffer:
            content = upload_file.file.read()
            buffer.write(content)

        logger.info(f"File saved successfully: {destination_path}")
        return True, None

    except Exception as e:
        error_msg = f"Failed to save file: {str(e)}"
        logger.error(error_msg)
        return False, error_msg


def cleanup_file(file_path: Path) -> None:
    """Clean up temporary file"""
    try:
        if file_path.exists():
            file_path.unlink()
            logger.debug(f"Cleaned up file: {file_path}")
    except Exception as e:
        logger.warning(f"Failed to cleanup file {file_path}: {e}")


def validate_file_path(file_path: str) -> Tuple[bool, Optional[str], Optional[Path]]:
    """Validate and resolve file path"""
    try:
        path = Path(file_path).resolve()

        # Security check - prevent directory traversal
        if ".." in str(path) or not path.is_relative_to(Path.cwd()):
            return False, "Invalid file path - directory traversal detected", None

        if not path.exists():
            return False, f"File not found: {file_path}", None

        if not path.is_file():
            return False, f"Path is not a file: {file_path}", None

        return True, None, path

    except Exception as e:
        return False, f"Path validation error: {str(e)}", None


def get_file_info(file_path: Path) -> dict:
    """Get file information"""
    try:
        stat = file_path.stat()
        return {
            "name": file_path.name,
            "size": stat.st_size,
            "modified": stat.st_mtime,
            "extension": file_path.suffix,
            "path": str(file_path)
        }
    except Exception as e:
        logger.error(f"Failed to get file info: {e}")
        return {}


def is_safe_filename(filename: str) -> bool:
    """Check if filename is safe (no dangerous characters)"""
    dangerous_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|', '\0']
    return not any(char in filename for char in dangerous_chars)
