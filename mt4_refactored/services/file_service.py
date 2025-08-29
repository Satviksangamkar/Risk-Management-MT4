"""
File Service for MT4 Parser
Handles all file operations including loading, validation, and processing.
"""

from pathlib import Path
from typing import Optional

from ..core.interfaces import IFileProcessor
from ..core.exceptions import MT4FileError
from ..config import MT4Config
from ..utils import LoggerMixin


class FileService(LoggerMixin, IFileProcessor):
    """
    Service for handling file operations.

    Provides safe file loading, validation, and encoding detection.
    Implements the IFileProcessor interface.
    """

    def __init__(self, config: Optional[MT4Config] = None):
        """
        Initialize the file service.

        Args:
            config: Configuration object
        """
        self.config = config or MT4Config()

    def validate_file(self, file_path: Path) -> bool:
        """
        Validate file exists, has correct extension, and is readable.

        Args:
            file_path: Path to the file to validate

        Returns:
            bool: True if file is valid

        Raises:
            MT4FileError: If validation fails
        """
        try:
            # Check if file exists
            if not file_path.exists():
                raise MT4FileError(f"File does not exist: {file_path}")

            # Check if it's a file (not directory)
            if not file_path.is_file():
                raise MT4FileError(f"Path is not a file: {file_path}")

            # Check file extension
            if not self.config.validate_file_extension(file_path):
                raise MT4FileError(
                    f"Invalid file extension. Expected: {self.config.SUPPORTED_EXTENSIONS}, "
                    f"Got: {file_path.suffix}"
                )

            # Check file size (prevent extremely large files)
            file_size = file_path.stat().st_size
            if file_size == 0:
                raise MT4FileError(f"File is empty: {file_path}")
            if file_size > self.config.MAX_FILE_SIZE_MB * 1024 * 1024:
                raise MT4FileError(
                    f"File too large: {file_size} bytes. "
                    f"Maximum allowed: {self.config.MAX_FILE_SIZE_MB}MB"
                )

            self.log_debug(f"File validation passed: {file_path}")
            return True

        except MT4FileError:
            raise
        except Exception as e:
            raise MT4FileError(f"File validation failed: {str(e)}") from e

    def load_file(self, file_path: Path) -> str:
        """
        Load file content with proper encoding detection.

        Args:
            file_path: Path to the file to load

        Returns:
            str: File content as string

        Raises:
            MT4FileError: If file loading fails
        """
        try:
            # Validate file first
            self.validate_file(file_path)

            # Try primary encoding first
            try:
                with open(file_path, 'r', encoding=self.config.DEFAULT_ENCODING) as file:
                    content = file.read()
                self.log_info(f"Successfully loaded file with {self.config.DEFAULT_ENCODING}: {file_path}")
                return content

            except UnicodeDecodeError:
                # Fallback to alternative encoding
                self.log_warning(f"Failed to decode with {self.config.DEFAULT_ENCODING}, trying fallback")
                with open(file_path, 'r', encoding=self.config.FALLBACK_ENCODING,
                         errors=self.config.FALLBACK_ENCODING) as file:
                    content = file.read()
                self.log_info(f"Successfully loaded file with fallback encoding: {file_path}")
                return content

        except MT4FileError:
            raise
        except Exception as e:
            raise MT4FileError(f"Failed to load file {file_path}: {str(e)}") from e

    def get_file_info(self, file_path: Path) -> dict:
        """
        Get detailed file information.

        Args:
            file_path: Path to the file

        Returns:
            dict: File information including size, encoding, etc.
        """
        try:
            stat = file_path.stat()
            return {
                'path': str(file_path),
                'name': file_path.name,
                'size_bytes': stat.st_size,
                'size_mb': round(stat.st_size / (1024 * 1024), 2),
                'extension': file_path.suffix,
                'last_modified': stat.st_mtime
            }
        except Exception as e:
            self.log_error(f"Failed to get file info: {e}")
            return {}

