# core/bulk_upload_helpers.py
# Helper functions for safe bulk upload

import re
from datetime import datetime


def safe_int_convert(value, default=0):
    """Safely convert a value to integer"""
    if value is None:
        return default
    if isinstance(value, int):
        return value
    if isinstance(value, (float, str)):
        try:
            if isinstance(value, str):
                # Remove non-numeric characters
                cleaned = re.sub(r"[^\d]", "", value)
                if cleaned:
                    return int(cleaned)
            else:
                return int(value)
        except (ValueError, TypeError):
            return default
    return default


def safe_year_convert(value):
    """Safely convert a year value"""
    current_year = datetime.now().year
    year = safe_int_convert(value, current_year)
    # Validate year is reasonable (between 2000 and 2100)
    if year < 2000 or year > 2100:
        return current_year
    return year


def validate_admission_number(value):
    """Validate admission number format"""
    if not value:
        return False
    value = str(value).strip()
    return bool(re.match(r"^[A-Za-z0-9]{4,20}$", value))
