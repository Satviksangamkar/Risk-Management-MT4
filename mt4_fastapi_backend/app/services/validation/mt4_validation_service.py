"""
MT4 Validation Service
Data validation and error handling for MT4 processing
"""

import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

from app.models.domain.mt4_models import TradeData, MT4StatementData, TradeType
from app.core.logging import get_logger
from app.core.config import settings

logger = get_logger(__name__)


class MT4ValidationService:
    """Service for validating MT4 data and files"""

    def __init__(self):
        self.allowed_extensions = {'.htm', '.html'}
        self.max_file_size = settings.MAX_UPLOAD_SIZE
        self.max_trades = settings.MAX_TRADES_PER_REQUEST

    def validate_file(self, file_path: Path) -> Tuple[bool, Optional[str]]:
        """
        Validate MT4 HTML file
        Returns (is_valid, error_message)
        """
        try:
            # Check if file exists
            if not file_path.exists():
                return False, f"File not found: {file_path}"

            # Check if it's a file
            if not file_path.is_file():
                return False, f"Path is not a file: {file_path}"

            # Check file extension
            if file_path.suffix.lower() not in self.allowed_extensions:
                return False, f"Invalid file extension. Allowed: {', '.join(self.allowed_extensions)}"

            # Check file size
            file_size = file_path.stat().st_size
            if file_size == 0:
                return False, "File is empty"
            elif file_size > self.max_file_size:
                return False, f"File too large. Maximum size: {self.max_file_size / (1024*1024):.1f}MB"

            # Basic HTML validation
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            if not self._is_valid_html(content):
                return False, "Invalid HTML content"

            return True, None

        except Exception as e:
            logger.error(f"File validation error: {e}")
            return False, f"Validation error: {str(e)}"

    def validate_trades_data(self, trades: List[TradeData]) -> Tuple[bool, List[str]]:
        """
        Validate trades data
        Returns (is_valid, error_messages)
        """
        errors = []

        if not trades:
            errors.append("No trades found")
            return False, errors

        if len(trades) > self.max_trades:
            errors.append(f"Too many trades. Maximum allowed: {self.max_trades}")
            return False, errors

        # Validate individual trades
        for i, trade in enumerate(trades):
            trade_errors = self._validate_single_trade(trade, i)
            errors.extend(trade_errors)

        return len(errors) == 0, errors

    def validate_statement_data(self, data: MT4StatementData) -> Tuple[bool, List[str]]:
        """
        Validate complete statement data
        Returns (is_valid, error_messages)
        """
        errors = []

        # Validate account info
        if not data.account_info.is_complete():
            errors.append("Incomplete account information")

        # Validate financial summary
        financial_errors = self._validate_financial_summary(data.financial_summary)
        errors.extend(financial_errors)

        # Validate trades
        trades_valid, trade_errors = self.validate_trades_data(data.closed_trades + data.open_trades)
        if not trades_valid:
            errors.extend(trade_errors)

        return len(errors) == 0, errors

    def _validate_single_trade(self, trade: TradeData, index: int) -> List[str]:
        """Validate a single trade"""
        errors = []
        prefix = f"Trade {index + 1}:"

        # Required fields validation
        if not trade.ticket:
            errors.append(f"{prefix} Missing ticket number")

        if not trade.type:
            errors.append(f"{prefix} Missing trade type")
        elif trade.type not in [TradeType.BUY, TradeType.SELL]:
            errors.append(f"{prefix} Invalid trade type: {trade.type}")

        # Numeric field validation
        if trade.size <= 0:
            errors.append(f"{prefix} Invalid trade size: {trade.size}")

        if trade.price <= 0:
            errors.append(f"{prefix} Invalid entry price: {trade.price}")

        # Stop loss validation
        if trade.s_l <= 0:
            errors.append(f"{prefix} Invalid stop loss: {trade.s_l}")

        # Trade type specific validation
        if trade.type == TradeType.BUY and trade.s_l >= trade.price:
            errors.append(f"{prefix} Buy trade stop loss should be below entry price")
        elif trade.type == TradeType.SELL and trade.s_l <= trade.price:
            errors.append(f"{prefix} Sell trade stop loss should be above entry price")

        # Closed trade validation
        if trade.is_closed_trade:
            if trade.close_price <= 0:
                errors.append(f"{prefix} Invalid close price: {trade.close_price}")
            if not trade.close_time:
                errors.append(f"{prefix} Missing close time")

        return errors

    def _validate_financial_summary(self, financial_summary) -> List[str]:
        """Validate financial summary data"""
        errors = []

        # Balance should be reasonable
        if financial_summary.balance < -1000000 or financial_summary.balance > 10000000:
            errors.append("Suspicious balance amount")

        # Equity should not be negative (except in extreme cases)
        if financial_summary.equity < -10000:
            errors.append("Suspicious negative equity")

        # Margin validation
        if financial_summary.margin < 0:
            errors.append("Negative margin not allowed")

        return errors

    def _is_valid_html(self, content: str) -> bool:
        """Basic HTML validation"""
        if not content or len(content.strip()) < 100:
            return False

        # Check for basic HTML structure
        content_lower = content.lower()

        # Should contain basic HTML tags
        required_tags = ['<html', '<body', '<table']
        optional_tags = ['<head', '<title', '<tr', '<td']

        required_count = sum(1 for tag in required_tags if tag in content_lower)
        optional_count = sum(1 for tag in optional_tags if tag in content_lower)

        # Must have at least 2 required tags and 1 optional tag
        return required_count >= 2 and (required_count + optional_count) >= 3

    def sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for security"""
        # Remove path separators and dangerous characters
        dangerous_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        sanitized = filename

        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '_')

        # Limit length
        if len(sanitized) > 100:
            name, ext = sanitized.rsplit('.', 1) if '.' in sanitized else (sanitized, '')
            if ext:
                sanitized = name[:95] + '.' + ext
            else:
                sanitized = sanitized[:100]

        return sanitized

    def validate_url(self, url: str) -> Tuple[bool, Optional[str]]:
        """Validate URL for MT4 statement download"""
        if not url:
            return False, "URL is required"

        # Basic URL validation
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)

        if not url_pattern.match(url):
            return False, "Invalid URL format"

        # Check for suspicious patterns
        suspicious_patterns = [
            r'\.\./',  # directory traversal
            r'javascript:',  # javascript URLs
            r'data:',  # data URLs
            r'vbscript:',  # vbscript URLs
        ]

        for pattern in suspicious_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return False, "Suspicious URL pattern detected"

        return True, None
