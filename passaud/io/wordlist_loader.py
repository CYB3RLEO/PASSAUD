"""
Wordlist loading functionality for PassAud.
"""

import logging
from pathlib import Path
from typing import Generator, List

logger = logging.getLogger(__name__)

class WordlistLoader:
    """Load and stream wordlists."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def stream_wordlist(self, path: str, max_words: int = None) -> Generator[str, None, None]:
        """Stream words from a wordlist file."""
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Wordlist not found: {path}")
        
        if not path.is_file():
            raise ValueError(f"Path is not a file: {path}")
        
        try:
            with open(path, "r", errors="ignore", encoding="latin-1") as f:
                for i, line in enumerate(f):
                    if max_words is not None and i >= max_words:
                        break
                    word = line.strip()
                    if word:
                        yield word
        except Exception as e:
            self.logger.error(f"Error reading wordlist: {e}")
            raise
    
    def load_wordlist(self, path: str, max_words: int = None) -> List[str]:
        """Load a wordlist into memory."""
        return list(self.stream_wordlist(path, max_words))