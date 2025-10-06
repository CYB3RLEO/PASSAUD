"""
Password analysis functionality for PassAud.
"""

import logging
import math
import re
import string
from typing import Dict, Any, List
import hashlib

logger = logging.getLogger(__name__)

class PasswordAnalyzer:
    """Analyze password strength and characteristics."""
    
    def __init__(self, config_manager=None):
        self.config_manager = config_manager
        self.logger = logging.getLogger(__name__)
        
        # Common passwords and names (in production, load from files)
        self.common_passwords = [
            "password", "123456", "admin", "qwerty", "letmein",
            "welcome", "monkey", "sunshine", "password1", "123456789"
        ]
        
        self.common_names = [
            "john", "jane", "smith", "doe", "david", "michael", "sarah"
        ]
    
    def analyze(self, password: str) -> Dict[str, Any]:
        """Comprehensive password strength analysis."""
        if not isinstance(password, str):
            return {
                "error": "Password must be a string",
                "score": 0,
                "rating": "Invalid"
            }
        
        if len(password) > 1000:
            return {
                "error": "Password is too long (max 1000 characters)",
                "score": 0,
                "rating": "Invalid"
            }
        
        result = {
            "score": 0,
            "length": len(password),
            "feedback": [],
            "vulnerabilities": [],
            "entropy": 0,
            "sequences": [],
            "personal_info": [],
            "rating": "Very Weak"
        }
        
        # Length analysis
        if len(password) < 8:
            result["vulnerabilities"].append("CRITICAL: Password too short (<8 chars)")
            result["feedback"].append("Minimum 12 characters recommended")
        elif len(password) < 12:
            result["vulnerabilities"].append("WARNING: Password short (8-11 chars)")
            result["feedback"].append("Increase length to 12+ characters")
        else:
            result["score"] += 1 if len(password) < 16 else 2
        
        # Complexity checks
        complexity_flags = {
            "digit": r'\d',
            "uppercase": r'[A-Z]',
            "lowercase": r'[a-z]',
            "special": r'[!@#$%^&*()_+{}\[\]:;<>,.?~\\-]'
        }
        
        for name, pattern in complexity_flags.items():
            if re.search(pattern, password):
                result["score"] += 1
            else:
                result["feedback"].append(f"Missing {name} character")
        
        # Common password check
        if password.lower() in self.common_passwords:
            result["score"] = max(1, result["score"] - 2)
            result["vulnerabilities"].append("CRITICAL: Common password detected")
            result["feedback"].append("Avoid dictionary words and predictable sequences")
        
        # Entropy calculation
        result["entropy"] = self._calculate_entropy(password)
        if result["entropy"] < 40:
            result["vulnerabilities"].append(f"Low entropy: {result['entropy']} bits (aim for 60+ bits)")
        elif result["entropy"] < 60:
            result["vulnerabilities"].append(f"Medium entropy: {result['entropy']} bits (aim for 60+ bits)")
        
        # Sequence detection
        result["sequences"] = self._detect_sequences(password)
        if result["sequences"]:
            result["score"] = max(1, result["score"] - 1)
            result["vulnerabilities"].append("Sequential characters detected")
        
        # Personal information detection
        result["personal_info"] = self._detect_personal_info(password)
        if result["personal_info"]:
            result["score"] = max(1, result["score"] - 1)
            result["vulnerabilities"].append("Personal information detected")
        
        # Rating assignment
        ratings = {
            5: "Excellent (Secure)",
            4: "Strong",
            3: "Medium (Improve)",
            2: "Weak",
            1: "Very Weak (Compromised)"
        }
        result["rating"] = ratings.get(result["score"], "Critical Failure")
        
        return result
    
    def _calculate_entropy(self, password: str) -> float:
        """Calculate password entropy in bits."""
        if not password:
            return 0.0
        
        charset_size = 0
        if any(c in string.ascii_lowercase for c in password):
            charset_size += 26
        if any(c in string.ascii_uppercase for c in password):
            charset_size += 26
        if any(c in string.digits for c in password):
            charset_size += 10
        if any(c in string.punctuation for c in password):
            charset_size += 32
        
        if charset_size == 0:
            charset_size = 94
        
        entropy = len(password) * math.log2(charset_size)
        return round(entropy, 2)
    
    def _detect_sequences(self, password: str) -> List[str]:
        """Detect sequential characters in password."""
        sequences = []
        
        keyboard_rows = [
            "qwertyuiop", "asdfghjkl", "zxcvbnm",
            "1234567890", "!@#$%^&*()"
        ]
        
        for i in range(len(password) - 2):
            segment = password[i:i+3].lower()
            
            for row in keyboard_rows:
                if segment in row:
                    sequences.append(f"Keyboard sequence: {segment}")
                    break
            
            for row in keyboard_rows:
                if segment[::-1] in row:
                    sequences.append(f"Reverse keyboard sequence: {segment}")
                    break
            
            if segment.isdigit():
                if segment in "1234567890" or segment in "0987654321":
                    sequences.append(f"Numerical sequence: {segment}")
        
        return sequences
    
    def _detect_personal_info(self, password: str) -> List[str]:
        """Detect potential personal information in password."""
        personal_info = []
        
        password_lower = password.lower()
        for name in self.common_names:
            if name in password_lower:
                personal_info.append(f"Contains common name: {name}")
        
        year_pattern = r"(19[7-9][0-9]|20[0-2][0-9])"
        years = re.findall(year_pattern, password)
        for year in years:
            personal_info.append(f"Contains year: {year}")
        
        date_pattern = r"(0[1-9]|1[0-2])(0[1-9]|[12][0-9]|3[01])"
        dates = re.findall(date_pattern, password)
        for date in dates:
            personal_info.append(f"Contains date pattern: {date}")
        
        return personal_info
    
    def estimate_bruteforce(self, password: str, speed: int = 1000000) -> Dict[str, Any]:
        """Brute-force time estimation for security reports."""
        if not password:
            return {"error": "Password cannot be empty"}
        
        charset = ""
        if any(c in string.ascii_lowercase for c in password):
            charset += string.ascii_lowercase
        if any(c in string.ascii_uppercase for c in password):
            charset += string.ascii_uppercase
        if any(c in string.digits for c in password):
            charset += string.digits
        if any(c in string.punctuation for c in password):
            charset += string.punctuation
        
        charset_size = len(charset) if charset else 94
        combinations = charset_size ** len(password)
        
        try:
            time_seconds = combinations / speed
        except ZeroDivisionError:
            return {"error": "Speed cannot be zero"}
        
        time_units = [
            (1, "seconds"),
            (60, "minutes"),
            (3600, "hours"),
            (86400, "days"),
            (2592000, "months"),
            (31536000, "years"),
            (3153600000, "centuries")
        ]
        
        for divisor, unit in reversed(time_units):
            if time_seconds >= divisor:
                value = time_seconds / divisor
                return {
                    "time_estimate": f"{value:.1f} {unit}",
                    "combinations": f"{combinations:.2e}",
                    "charset_size": charset_size,
                    "password_length": len(password),
                    "cracking_speed": f"{speed} attempts/sec",
                    "character_sets": list(filter(None, {
                        "lower" if any(c in string.ascii_lowercase for c in password) else None,
                        "upper" if any(c in string.ascii_uppercase for c in password) else None,
                        "digits" if any(c in string.digits for c in password) else None,
                        "special" if any(c in string.punctuation for c in password) else None
                    })),
                    "note": "This is a theoretical estimate. Actual time may vary significantly."
                }
        
        return {"time_estimate": "Instant"}
    
    def detect_hash_type(self, hash_str: str) -> str:
        """Auto-detect hash type based on length and character set."""
        if not hash_str:
            return None
        
        hash_str = hash_str.strip().lower()
        
        if hash_str.startswith('0x'):
            hash_str = hash_str[2:]
        elif hash_str.startswith('$') and '$' in hash_str[1:]:
            if hash_str.startswith('$2a$') or hash_str.startswith('$2b$') or hash_str.startswith('$2y$'):
                return "bcrypt"
            elif hash_str.startswith('$5$'):
                return "sha256"
            elif hash_str.startswith('$6$'):
                return "sha512"
            elif hash_str.startswith('$argon2'):
                return "argon2"
            else:
                return None
        
        if not all(c in "0123456789abcdef" for c in hash_str):
            if hash_str.startswith('$2'):
                return "bcrypt"
            return None
        
        length = len(hash_str)
        if length == 32:
            return "md5"
        elif length == 40:
            return "sha1"
        elif length == 64:
            return "sha256"
        elif length == 96:
            return "sha384"
        elif length == 128:
            return "sha512"
        elif length >= 64 and length <= 256:
            return "scrypt"
        return None