"""
Core interfaces for MT4 Parser
Defines contracts for different components.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pathlib import Path

try:
    # Try relative imports first (for package usage)
    from ..models import MT4StatementData
except ImportError:
    # Fall back to absolute imports (for direct execution)
    from models.data_models import MT4StatementData


class IParser(ABC):
    """Interface for all parsers."""

    @abstractmethod
    def parse(self) -> Any:
        """Parse data and return structured result."""
        pass

    @abstractmethod
    def validate(self) -> bool:
        """Validate parsed data."""
        pass


class ICalculator(ABC):
    """Interface for calculation services."""

    @abstractmethod
    def calculate(self, data: Any) -> Any:
        """Perform calculations on provided data."""
        pass

    @abstractmethod
    def validate_input(self, data: Any) -> bool:
        """Validate input data for calculations."""
        pass


class IService(ABC):
    """Interface for all services."""

    @abstractmethod
    def process(self, data: Any) -> Any:
        """Process data and return result."""
        pass

    @abstractmethod
    def get_name(self) -> str:
        """Get service name."""
        pass


class IRepository(ABC):
    """Interface for data repositories."""

    @abstractmethod
    def save(self, data: Any) -> bool:
        """Save data to repository."""
        pass

    @abstractmethod
    def load(self, identifier: Any) -> Optional[Any]:
        """Load data from repository."""
        pass


class IFileProcessor(ABC):
    """Interface for file processing operations."""

    @abstractmethod
    def load_file(self, file_path: Path) -> str:
        """Load file content."""
        pass

    @abstractmethod
    def validate_file(self, file_path: Path) -> bool:
        """Validate file format and content."""
        pass
