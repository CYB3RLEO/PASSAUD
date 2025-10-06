"""
Comprehensive hash management functionality for PassAud.
"""

import hashlib
import logging
import os
import base64
from typing import Optional, Dict, Any, List
import bcrypt
import argon2
import scrypt
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

logger = logging.getLogger(__name__)

class HashManager:
    """Comprehensive hash management with multiple algorithms."""
    
    def __init__(self, config_manager=None):
        self.config_manager = config_manager
        self.logger = logging.getLogger(__name__)
    
    def hash_string(self, input_str: str, algorithm: str = "md5") -> Optional[str]:
        """Generate hash for a string with comprehensive algorithm support."""
        try:
            algorithm = algorithm.lower()
            
            if algorithm == "md5":
                return hashlib.md5(input_str.encode()).hexdigest()
            elif algorithm == "sha1":
                return hashlib.sha1(input_str.encode()).hexdigest()
            elif algorithm == "sha256":
                return hashlib.sha256(input_str.encode()).hexdigest()
            elif algorithm == "sha384":
                return hashlib.sha384(input_str.encode()).hexdigest()
            elif algorithm == "sha512":
                return hashlib.sha512(input_str.encode()).hexdigest()
            elif algorithm == "bcrypt":
                salt = bcrypt.gensalt()
                return bcrypt.hashpw(input_str.encode(), salt).decode()
            elif algorithm == "scrypt":
                salt = os.urandom(16)
                hashed = scrypt.hash(input_str.encode(), salt, N=16384, r=8, p=1)
                return hashed.hex()
            elif algorithm == "argon2":
                hasher = argon2.PasswordHasher()
                return hasher.hash(input_str)
            elif algorithm == "pbkdf2_sha256":
                salt = os.urandom(16)
                kdf = PBKDF2HMAC(
                    algorithm=hashes.SHA256(),
                    length=32,
                    salt=salt,
                    iterations=100000,
                )
                key = base64.urlsafe_b64encode(kdf.derive(input_str.encode()))
                return key.decode()
            else:
                raise ValueError(f"Unsupported algorithm: {algorithm}")
                
        except Exception as e:
            self.logger.error(f"Error hashing string with {algorithm}: {e}")
            return None
    
    def verify_hash(self, input_str: str, hash_value: str, algorithm: str = None) -> bool:
        """Verify if input string matches the hash."""
        try:
            # If algorithm not specified, try to detect it
            if not algorithm:
                from passaud.core.analyzer import PasswordAnalyzer
                analyzer = PasswordAnalyzer()
                algorithm = analyzer.detect_hash_type(hash_value)
                if not algorithm:
                    return False
            
            if algorithm == "bcrypt":
                return bcrypt.checkpw(input_str.encode(), hash_value.encode())
            elif algorithm == "argon2":
                hasher = argon2.PasswordHasher()
                try:
                    hasher.verify(hash_value, input_str)
                    return True
                except argon2.exceptions.VerifyMismatchError:
                    return False
            else:
                # For other algorithms, compute hash and compare
                computed_hash = self.hash_string(input_str, algorithm)
                return computed_hash == hash_value
                
        except Exception as e:
            self.logger.error(f"Error verifying hash: {e}")
            return False
    
    def hash_batch(self, strings: List[str], algorithm: str = "md5") -> List[str]:
        """Hash a batch of strings efficiently."""
        results = []
        for s in strings:
            results.append(self.hash_string(s, algorithm))
        return results
    
    def get_hash_info(self, hash_value: str) -> Dict[str, Any]:
        """Get information about a hash."""
        from passaud.core.analyzer import PasswordAnalyzer
        analyzer = PasswordAnalyzer()
        
        hash_type = analyzer.detect_hash_type(hash_value)
        info = {
            "hash": hash_value,
            "type": hash_type,
            "length": len(hash_value),
            "is_hex": all(c in "0123456789abcdefABCDEF" for c in hash_value)
        }
        
        # Add algorithm-specific info
        if hash_type == "md5":
            info["bits"] = 128
            info["collision_resistant"] = False
        elif hash_type == "sha1":
            info["bits"] = 160
            info["collision_resistant"] = False
        elif hash_type == "sha256":
            info["bits"] = 256
            info["collision_resistant"] = True
        elif hash_type == "sha512":
            info["bits"] = 512
            info["collision_resistant"] = True
        elif hash_type == "bcrypt":
            info["bits"] = 184
            info["adaptive"] = True
        
        return info