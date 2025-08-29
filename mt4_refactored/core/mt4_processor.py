"""
Refactored MT4 Processor - Industry Standard Edition
Clean, modular orchestrator for MT4 statement processing.
"""

from pathlib import Path
from typing import Optional, Dict, Any
import sys
import os

# Robust import system for both package and direct execution
current_dir = os.path.dirname(__file__)
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

try:
    # Try package imports first
    from mt4_refactored.core.interfaces import IFileProcessor
    from mt4_refactored.core.exceptions import (
        MT4ProcessingError,
        MT4ValidationError,
        MT4FileError
    )
    from mt4_refactored.config.settings import MT4Config
    from mt4_refactored.models.data_models import MT4StatementData
    from mt4_refactored.utils.logging_utils import LoggerMixin, ProgressLogger
except ImportError:
    try:
        # Try direct module imports
        from core.interfaces import IFileProcessor
        from core.exceptions import (
            MT4ProcessingError,
            MT4ValidationError,
            MT4FileError
        )
        from config.settings import MT4Config
        from models.data_models import MT4StatementData
        from utils.logging_utils import LoggerMixin, ProgressLogger
    except ImportError as e:
        print(f"MT4Processor import error: {e}")
        # Define fallback classes
        class IFileProcessor: pass
        class MT4ProcessingError(Exception): pass
        class MT4ValidationError(Exception): pass
        class MT4FileError(Exception): pass
        class MT4Config: pass
        class MT4StatementData: pass
        class LoggerMixin: pass
        class ProgressLogger: pass

# Lazy import functions to avoid circular dependencies
def _get_service(service_name):
    """Get a service class by name to avoid circular imports."""
    try:
        if service_name == 'parsing':
            from mt4_refactored.services.parsing_service import ParsingService
            return ParsingService
        elif service_name == 'calculation':
            from mt4_refactored.services.calculation_service import CalculationService
            return CalculationService
        elif service_name == 'validation':
            from mt4_refactored.services.validation_service import ValidationService
            return ValidationService
    except ImportError:
        try:
            if service_name == 'parsing':
                from services.parsing_service import ParsingService
                return ParsingService
            elif service_name == 'calculation':
                from services.calculation_service import CalculationService
                return CalculationService
            elif service_name == 'validation':
                from services.validation_service import ValidationService
                return ValidationService
        except ImportError as e:
            print(f"Service import error for {service_name}: {e}")
            return None
    return None


class MT4Processor(LoggerMixin):
    """
    Main processor for MT4 HTML statements.

    Clean orchestrator that delegates to specialized services.
    Follows single responsibility principle and dependency injection.
    """

    def __init__(
        self,
        config: Optional[MT4Config] = None,
        parsing_service: Optional['ParsingService'] = None,
        calculation_service: Optional['CalculationService'] = None,
        validation_service: Optional['ValidationService'] = None,
        file_processor: Optional[IFileProcessor] = None
    ):
        """
        Initialize the MT4 processor with dependency injection.

        Args:
            config: Configuration object
            parsing_service: Service for parsing HTML content
            calculation_service: Service for calculations
            validation_service: Service for validation
            file_processor: Service for file operations
        """
        self.config = config or MT4Config()

        # Initialize services with dependency injection
        self._parsing_service = parsing_service
        self._calculation_service = calculation_service
        self._validation_service = validation_service
        self._file_processor = file_processor

        # Lazy initialization flags
        self._services_initialized = False

        self.log_info("MT4 Processor initialized with industry-standard architecture")

    def _initialize_services(self) -> None:
        """Lazy initialization of services."""
        if self._services_initialized:
            return

        # Initialize services if not provided
        if not self._parsing_service:
            ParsingService = _get_service('parsing')
            self._parsing_service = ParsingService(self.config)
        if not self._calculation_service:
            CalculationService = _get_service('calculation')
            self._calculation_service = CalculationService(self.config)
        if not self._validation_service:
            ValidationService = _get_service('validation')
            self._validation_service = ValidationService(self.config)
        if not self._file_processor:
            try:
                from services.file_service import FileService
                self._file_processor = FileService(self.config)
            except ImportError:
                # Create a dummy file processor if not available
                from utils.logging_utils import LoggerMixin
                class DummyFileProcessor(LoggerMixin):
                    def __init__(self, config): self.config = config
                    def load_file(self, path): return open(path, 'r', encoding='utf-8').read()
                    def validate_file(self, path): return path.exists()
                self._file_processor = DummyFileProcessor(self.config)

        self._services_initialized = True

    def process_file(self, file_path: Path) -> MT4StatementData:
        """
        Process an MT4 HTML file using the service-oriented architecture.

        Args:
            file_path: Path to the HTML file

        Returns:
            MT4StatementData: Complete structured data

        Raises:
            MT4FileError: If file operations fail
            MT4ValidationError: If data validation fails
            MT4ProcessingError: For general processing errors
        """
        try:
            self.log_info(f"Starting MT4 file processing: {file_path}")
            self._initialize_services()

            # Create progress logger
            progress = ProgressLogger("MT4 statement processing", 5)

            # Step 1: Validate and load file
            progress.start()
            progress.log_section("File Validation & Loading")

            if not self._file_processor.validate_file(file_path):
                raise MT4FileError(f"Invalid file format: {file_path}")

            html_content = self._file_processor.load_file(file_path)
            progress.update()

            # Step 2: Parse HTML content
            progress.log_section("HTML Parsing")
            parsed_data = self._parsing_service.process(html_content)
            progress.update()

            # Step 3: Validate parsed data
            progress.log_section("Data Validation")
            validation_result = self._validation_service.process(parsed_data)
            if not validation_result['is_valid']:
                raise MT4ValidationError(f"Data validation failed: {validation_result['issues']}")
            progress.update()

            # Step 4: Perform calculations
            progress.log_section("Calculations & Analytics")
            calculated_data = self._calculation_service.process(parsed_data)
            progress.update()

            # Step 5: Final assembly and validation
            progress.log_section("Final Assembly")
            final_data = self._assemble_final_data(parsed_data, calculated_data)
            progress.update()

            progress.complete()
            self.log_info("MT4 file processing completed successfully")

            return final_data

        except (MT4FileError, MT4ValidationError, MT4ProcessingError):
            raise
        except Exception as e:
            self.log_error(f"Unexpected error during processing: {e}")
            raise MT4ProcessingError(f"Processing failed: {str(e)}", details=e) from e

    def _assemble_final_data(
        self,
        parsed_data: Dict[str, Any],
        calculated_data: Dict[str, Any]
    ) -> MT4StatementData:
        """
        Assemble final MT4StatementData from parsed and calculated data.

        Args:
            parsed_data: Raw parsed data from services
            calculated_data: Calculated metrics and analytics

        Returns:
            MT4StatementData: Complete structured data object
        """
        # Create the final data object
        data = MT4StatementData()

        # Copy parsed data sections
        data.account_info = parsed_data.get('account_info')
        data.financial_summary = parsed_data.get('financial_summary')
        data.performance_metrics = parsed_data.get('performance_metrics')
        data.trade_statistics = parsed_data.get('trade_statistics')
        data.closed_trades = parsed_data.get('closed_trades', [])
        data.open_trades = parsed_data.get('open_trades', [])

        # Copy calculated data
        data.calculated_metrics = calculated_data.get('calculated_metrics')
        data.r_multiple_data = calculated_data.get('r_multiple_data', [])
        data.r_multiple_statistics = calculated_data.get('r_multiple_statistics')

        self.log_debug("Final data assembly completed")
        return data

    def get_processing_summary(self, data: MT4StatementData) -> Dict[str, Any]:
        """
        Generate a comprehensive processing summary.

        Args:
            data: Processed MT4 statement data

        Returns:
            Dict containing summary information
        """
        return {
            'file_info': {
                'total_trades': data.get_total_trades(),
                'closed_trades': len(data.closed_trades),
                'open_trades': len(data.open_trades),
                'total_profit': data.get_total_profit()
            },
            'performance': {
                'win_rate': data.calculated_metrics.win_rate if data.calculated_metrics else 0,
                'profit_factor': data.performance_metrics.profit_factor if data.performance_metrics else 0,
                'roi': data.calculated_metrics.roi_percentage if data.calculated_metrics else 0,
                'max_drawdown': data.performance_metrics.maximal_drawdown_percentage if data.performance_metrics else 0
            },
            'account': {
                'balance': data.financial_summary.balance if data.financial_summary else 0,
                'equity': data.financial_summary.equity if data.financial_summary else 0,
                'free_margin': data.financial_summary.free_margin if data.financial_summary else 0
            },
            'r_multiple': {
                'valid_r_trades': data.r_multiple_statistics.total_valid_r_trades if data.r_multiple_statistics else 0,
                'r_win_rate': data.r_multiple_statistics.r_win_rate if data.r_multiple_statistics else 0,
                'average_r_multiple': data.r_multiple_statistics.average_r_multiple if data.r_multiple_statistics else 0,
                'r_performance_rating': data.r_multiple_statistics.get_r_performance_rating() if data.r_multiple_statistics else "N/A"
            } if data.r_multiple_statistics and data.r_multiple_statistics.total_valid_r_trades > 0 else None
        }
