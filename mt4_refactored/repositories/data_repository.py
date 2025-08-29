"""
Data Repository for MT4 Parser
Handles data storage and retrieval operations.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional, List

from ..core.interfaces import IRepository
from ..core.exceptions import MT4ProcessingError
from ..config import MT4Config
from ..models import MT4StatementData
from ..utils import LoggerMixin


class DataRepository(LoggerMixin, IRepository):
    """
    Repository for managing MT4 statement data.

    Provides data persistence and retrieval capabilities including:
    - JSON serialization/deserialization
    - File-based storage
    - Data caching
    - Export/import operations
    """

    def __init__(self, config: Optional[MT4Config] = None, storage_path: Optional[Path] = None):
        """
        Initialize the data repository.

        Args:
            config: Configuration object
            storage_path: Path for data storage
        """
        self.config = config or MT4Config()
        self.storage_path = storage_path or Path("mt4_data")
        self.storage_path.mkdir(exist_ok=True)
        self._cache: Dict[str, MT4StatementData] = {}

        self.log_info(f"Data Repository initialized at {self.storage_path}")

    def save(self, data: MT4StatementData, identifier: Optional[str] = None) -> bool:
        """
        Save MT4 statement data to repository.

        Args:
            data: MT4StatementData object to save
            identifier: Optional identifier for the data

        Returns:
            bool: True if save was successful

        Raises:
            MT4ProcessingError: If save operation fails
        """
        try:
            # Generate identifier if not provided
            if not identifier:
                identifier = f"mt4_statement_{data.account_info.account_number}_{hash(str(data))}"

            # Convert to dictionary
            data_dict = data.to_dict()

            # Add metadata
            data_dict['_metadata'] = {
                'identifier': identifier,
                'timestamp': str(Path(identifier).stat().st_mtime) if Path(identifier).exists() else None,
                'version': '2.0.0'
            }

            # Save to file
            file_path = self.storage_path / f"{identifier}.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data_dict, f, indent=2, default=str)

            # Cache the data
            self._cache[identifier] = data

            self.log_info(f"Data saved successfully: {identifier}")
            return True

        except Exception as e:
            self.log_error(f"Failed to save data: {e}")
            raise MT4ProcessingError(f"Failed to save data: {str(e)}", details=e) from e

    def load(self, identifier: str) -> Optional[MT4StatementData]:
        """
        Load MT4 statement data from repository.

        Args:
            identifier: Identifier of the data to load

        Returns:
            MT4StatementData object or None if not found

        Raises:
            MT4ProcessingError: If load operation fails
        """
        try:
            # Check cache first
            if identifier in self._cache:
                return self._cache[identifier]

            # Load from file
            file_path = self.storage_path / f"{identifier}.json"
            if not file_path.exists():
                self.log_warning(f"Data file not found: {identifier}")
                return None

            with open(file_path, 'r', encoding='utf-8') as f:
                data_dict = json.load(f)

            # Remove metadata before creating object
            metadata = data_dict.pop('_metadata', {})

            # Create MT4StatementData object
            data = MT4StatementData()
            self._populate_from_dict(data, data_dict)

            # Cache the loaded data
            self._cache[identifier] = data

            self.log_info(f"Data loaded successfully: {identifier}")
            return data

        except Exception as e:
            self.log_error(f"Failed to load data {identifier}: {e}")
            raise MT4ProcessingError(f"Failed to load data: {str(e)}", details=e) from e

    def list_saved_data(self) -> List[str]:
        """
        List all saved data identifiers.

        Returns:
            List of data identifiers
        """
        try:
            identifiers = []
            for file_path in self.storage_path.glob("*.json"):
                if file_path.name.startswith("mt4_statement_"):
                    identifier = file_path.stem
                    identifiers.append(identifier)

            return identifiers

        except Exception as e:
            self.log_error(f"Failed to list saved data: {e}")
            return []

    def delete(self, identifier: str) -> bool:
        """
        Delete data from repository.

        Args:
            identifier: Identifier of the data to delete

        Returns:
            bool: True if deletion was successful
        """
        try:
            # Remove from cache
            if identifier in self._cache:
                del self._cache[identifier]

            # Delete file
            file_path = self.storage_path / f"{identifier}.json"
            if file_path.exists():
                file_path.unlink()
                self.log_info(f"Data deleted successfully: {identifier}")
                return True
            else:
                self.log_warning(f"Data file not found for deletion: {identifier}")
                return False

        except Exception as e:
            self.log_error(f"Failed to delete data {identifier}: {e}")
            return False

    def export_to_csv(self, data: MT4StatementData, output_path: Path) -> bool:
        """
        Export data to CSV format.

        Args:
            data: MT4StatementData to export
            output_path: Path for CSV output

        Returns:
            bool: True if export was successful
        """
        try:
            import csv

            # Export closed trades
            if data.closed_trades:
                trades_file = output_path / "closed_trades.csv"
                with open(trades_file, 'w', newline='', encoding='utf-8') as f:
                    if data.closed_trades:
                        writer = csv.DictWriter(f, fieldnames=data.closed_trades[0].__dict__.keys())
                        writer.writeheader()
                        for trade in data.closed_trades:
                            writer.writerow(trade.__dict__)

            # Export open trades
            if data.open_trades:
                open_trades_file = output_path / "open_trades.csv"
                with open(open_trades_file, 'w', newline='', encoding='utf-8') as f:
                    if data.open_trades:
                        writer = csv.DictWriter(f, fieldnames=data.open_trades[0].__dict__.keys())
                        writer.writeheader()
                        for trade in data.open_trades:
                            writer.writerow(trade.__dict__)

            self.log_info(f"Data exported to CSV: {output_path}")
            return True

        except Exception as e:
            self.log_error(f"Failed to export data to CSV: {e}")
            return False

    def _populate_from_dict(self, data: MT4StatementData, data_dict: Dict[str, Any]) -> None:
        """
        Populate MT4StatementData object from dictionary.

        Args:
            data: MT4StatementData object to populate
            data_dict: Dictionary containing data
        """
        # This is a simplified implementation
        # In a real-world scenario, you'd want more robust deserialization
        for key, value in data_dict.items():
            if hasattr(data, key):
                setattr(data, key, value)

