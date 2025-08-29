"""
Main MT4 Service
Orchestrates parsing, calculation, and validation services
"""

import time
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from datetime import datetime

from app.models.domain.mt4_models import MT4StatementData
from app.models.responses.mt4_responses import AnalysisResponse, ErrorResponse
from app.services.parsing.mt4_parser_service import MT4ParserService
from app.services.calculations.mt4_calculator_service import MT4CalculatorService
from app.services.validation.mt4_validation_service import MT4ValidationService
from app.core.logging import get_logger

logger = get_logger(__name__)


class MT4Service:
    """Main service for MT4 statement processing and analysis"""

    def __init__(self):
        self.parser = MT4ParserService()
        self.calculator = MT4CalculatorService()
        self.validator = MT4ValidationService()

    def process_statement_file(
        self,
        file_path: Path,
        calculate_r_multiple: bool = True,
        include_open_trades: bool = True
    ) -> Tuple[bool, Any]:
        """
        Process MT4 statement file
        Returns (success, response_data)
        """
        start_time = time.time()

        try:
            logger.info(f"Processing MT4 statement file: {file_path}")

            # Validate file
            is_valid, error_msg = self.validator.validate_file(file_path)
            if not is_valid:
                logger.error(f"File validation failed: {error_msg}")
                return False, ErrorResponse(
                    message="File validation failed",
                    error_code="VALIDATION_ERROR",
                    details={"error": error_msg}
                )

            # Read file content
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                html_content = f.read()

            # Parse HTML statement
            parsed_data = self.parser.parse_html_statement(html_content)

            # Create MT4StatementData object
            statement_data = MT4StatementData(
                account_info=parsed_data['account_info'],
                financial_summary=parsed_data['financial_summary'],
                performance_metrics=parsed_data['performance_metrics'],
                trade_statistics=parsed_data['trade_statistics'],
                closed_trades=parsed_data['closed_trades'],
                open_trades=parsed_data['open_trades']
            )

            # Validate parsed data
            is_valid, validation_errors = self.validator.validate_statement_data(statement_data)
            if not is_valid:
                logger.warning(f"Data validation issues: {validation_errors}")
                # Continue processing but log warnings

            # Calculate comprehensive metrics
            all_trades = statement_data.closed_trades + (statement_data.open_trades if include_open_trades else [])
            calculated_metrics = self.calculator.calculate_all_metrics(all_trades, calculate_r_multiple)
            statement_data.calculated_metrics = calculated_metrics

            # Calculate R-Multiple analysis if requested
            if calculate_r_multiple:
                r_trades, r_statistics = self.calculator.calculate_r_multiple_analysis(all_trades)
                statement_data.r_multiple_data = r_trades
                statement_data.r_multiple_statistics = r_statistics

            processing_time = time.time() - start_time
            total_trades = len(statement_data.closed_trades) + len(statement_data.open_trades)

            logger.info(f"Successfully processed {total_trades} trades in {processing_time:.2f}s")

            # Create response
            response = AnalysisResponse(
                data=statement_data,
                total_trades=total_trades,
                processing_time=processing_time,
                message="MT4 statement processed successfully"
            )

            return True, response

        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Processing failed after {processing_time:.2f}s: {str(e)}", exc_info=True)

            return False, ErrorResponse(
                message="Statement processing failed",
                error_code="PROCESSING_ERROR",
                details={"error": str(e), "processing_time": processing_time}
            )

    def process_statement_content(
        self,
        html_content: str,
        calculate_r_multiple: bool = True,
        include_open_trades: bool = True
    ) -> Tuple[bool, Any]:
        """
        Process MT4 statement from HTML content
        Returns (success, response_data)
        """
        start_time = time.time()

        try:
            logger.info("Processing MT4 statement from HTML content")

            # Parse HTML statement
            parsed_data = self.parser.parse_html_statement(html_content)

            # Create MT4StatementData object
            statement_data = MT4StatementData(
                account_info=parsed_data['account_info'],
                financial_summary=parsed_data['financial_summary'],
                performance_metrics=parsed_data['performance_metrics'],
                trade_statistics=parsed_data['trade_statistics'],
                closed_trades=parsed_data['closed_trades'],
                open_trades=parsed_data['open_trades']
            )

            # Calculate comprehensive metrics
            all_trades = statement_data.closed_trades + (statement_data.open_trades if include_open_trades else [])
            calculated_metrics = self.calculator.calculate_all_metrics(all_trades, calculate_r_multiple)
            statement_data.calculated_metrics = calculated_metrics

            # Calculate R-Multiple analysis if requested
            if calculate_r_multiple:
                r_trades, r_statistics = self.calculator.calculate_r_multiple_analysis(all_trades)
                statement_data.r_multiple_data = r_trades
                statement_data.r_multiple_statistics = r_statistics

            processing_time = time.time() - start_time
            total_trades = len(statement_data.closed_trades) + len(statement_data.open_trades)

            logger.info(f"Successfully processed {total_trades} trades in {processing_time:.2f}s")

            # Create response
            response = AnalysisResponse(
                data=statement_data,
                total_trades=total_trades,
                processing_time=processing_time,
                message="MT4 statement processed successfully"
            )

            return True, response

        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Content processing failed after {processing_time:.2f}s: {str(e)}", exc_info=True)

            return False, ErrorResponse(
                message="Content processing failed",
                error_code="PROCESSING_ERROR",
                details={"error": str(e), "processing_time": processing_time}
            )

    def get_health_status(self) -> Dict[str, Any]:
        """Get service health status"""
        return {
            "status": "healthy",
            "service": "MT4 Analysis Service",
            "timestamp": datetime.utcnow().isoformat(),
            "components": {
                "parser": "operational",
                "calculator": "operational",
                "validator": "operational"
            }
        }
