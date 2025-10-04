"""
Security-related utilities for PassAud.
"""

import ctypes
from typing import Any

def secure_erase(data: Any) -> None:
    """Securely erase data from memory."""
    if isinstance(data, str):
        data = data.encode('utf-8')
    if isinstance(data, bytes):
        # Overwrite the bytes
        length = len(data)
        ctypes.memset(ctypes.addressof(ctypes.c_char.from_buffer(data)), 0, length)
    # For other types, we cannot guarantee secure erasure in Python easily.

class SecureString:
    """A string that will be securely erased when deleted."""
    
    def __init__(self, string: str):
        self._data = string.encode('utf-8')
    
    def __str__(self) -> str:
        return self._data.decode('utf-8')
    
    def __del__(self):
        secure_erase(self._data)