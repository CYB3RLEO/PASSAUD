"""
Hash management functionality for PassAud.
"""

import hashlib
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class HashManager:
    """Manage hash operations."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def hash_string(self, input_str: str, algorithm: str = "md5") -> Optional[str]:
        """Generate hash for a string."""
        try:
            algorithm = algorithm.lower()
            if algorithm == "md5":
                return hashlib.md5(input_str.encode()).hexdigest()
            elif algorithm == "sha1":
                return hashlib.sha1(input_str.encode()).hexdigest()
            elif algorithm == "sha256":
                return hashlib.sha256(input_str.encode()).hexdigest()
            elif algorithm == "sha512":
                return hashlib.sha512(input_str.encode()).hexdigest()
            else:
                self.logger.error(f"Unsupported algorithm: {algorithm}")
                return None
        except Exception as e:
            self.logger.error(f"Error hashing string: {e}")
            return None