"""
Input validation for PassAud.
"""

import re
import os
import tempfile
from typing import Union

def validate_hash(hash_str: str) -> bool:
    """Validate if the string looks like a hash."""
    # Basic check: should be hexadecimal and of common lengths
    if not re.match(r'^[a-fA-F0-9]+$', hash_str):
        return False
    length = len(hash_str)
    # Common hash lengths: 32 (MD5), 40 (SHA1), 64 (SHA256), 96 (SHA384), 128 (SHA512)
    return length in [32, 40, 64, 96, 128]

def validate_file_path(path: str) -> bool:
    """Validate file path to prevent directory traversal."""
    try:
        # Convert to absolute path
        abs_path = os.path.abspath(path)
        # Check if path is within allowed directories
        allowed_dirs = [
            os.path.abspath("."),
            os.path.expanduser("~"),
            tempfile.gettempdir()
        ]
        
        for allowed_dir in allowed_dirs:
            if abs_path.startswith(allowed_dir):
                return True
                
        return False
    except Exception:
        return False