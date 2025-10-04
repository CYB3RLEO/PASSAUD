"""
Utility functions and classes for PassAud.
"""

from .logger import setup_logging
from .helpers import generate_random_string, chunk_list, safe_filename
from .validator import validate_hash, validate_file_path
from .security import secure_erase, SecureString

__all__ = [
    'setup_logging',
    'generate_random_string',
    'chunk_list',
    'safe_filename',
    'validate_hash',
    'validate_file_path',
    'secure_erase',
    'SecureString'
]