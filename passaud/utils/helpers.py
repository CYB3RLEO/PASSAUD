"""
Helper functions for PassAud.
"""

import os
import string
import random
from typing import List, Generator

def generate_random_string(length: int = 12) -> str:
    """Generate a random string of fixed length."""
    chars = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(chars) for _ in range(length))

def chunk_list(lst: List, chunk_size: int) -> Generator[List, None, None]:
    """Yield successive chunk_size chunks from lst."""
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]

def safe_filename(filename: str) -> str:
    """Convert a string to a safe filename."""
    keepchars = (' ', '.', '_', '-')
    return "".join(c for c in filename if c.isalnum() or c in keepchars).rstrip()