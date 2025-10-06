"""
Main password auditing class that coordinates all components.
"""

import logging
from typing import Dict, Any, Generator, List, Optional

from passaud.config.config_manager import ConfigManager
from passaud.core.analyzer import PasswordAnalyzer
from passaud.core.cracker import Cracker
from passaud.core.hasher import HashManager
from passaud.io.session_manager import SessionManager
from passaud.external.hibp_client import HIBPClient
from passaud.utils.rate_limiter import RateLimiter

logger = logging.getLogger(__name__)


class PasswordAuditor:
    """Main password auditing class with comprehensive security analysis."""

    def __init__(self, config_manager: ConfigManager = None):
        self.config_manager = config_manager or ConfigManager()
        self.analyzer = PasswordAnalyzer(self.config_manager)
        self.cracker = Cracker(self.config_manager)
        self.hasher = HashManager(self.config_manager)
        self.session_manager = SessionManager(self.config_manager)
        self.hibp_client = HIBPClient(
            self.config_manager.get('API_KEYS', 'hibp_api_key', ''),
            self.config_manager.get_float('DEFAULT', 'request_delay', 1.5)
        )
        self.rate_limiter = RateLimiter(
            self.config_manager.get_int(
                'DEFAULT', 'max_requests_per_minute', 30)
        )

        self.logger = logging.getLogger(__name__)

        # Load common passwords
        self.common_passwords = self._load_common_passwords()

    def _load_common_passwords(self) -> Generator[str, None, None]:
        """Load common passwords (simplified version)."""
        common = [
            "password", "123456", "admin", "qwerty", "letmein",
            "welcome", "monkey", "sunshine", "password1", "123456789"
        ]
        for pwd in common:
            yield pwd

    def analyze_strength(self, password: str) -> Dict[str, Any]:
        """Comprehensive password strength analysis with HIBP integration."""
        result = self.analyzer.analyze(password)

        # Add HIBP check
        try:
            hibp_count = self.hibp_client.check_password(password)
            if hibp_count > 0:
                result["score"] = max(1, result["score"] - 1)
                result["vulnerabilities"].append(
                    f"Password found in {hibp_count} data breaches (HIBP)")
                result["feedback"].append(
                    "This password has been compromised in data breaches")
        except Exception as e:
            self.logger.warning(f"HIBP check failed: {e}")

        # Save to session
        self.session_manager.add_result("strength", result, sensitive=True)

        return result

    def deep_dehash(self, hash_value: str, use_online: bool = False,
                    wordlist_path: str = None, max_words: int = 50000,
                    strategy: str = "auto") -> Dict[str, Any]:
        """Comprehensive hash cracking with multiple methods."""
        result = {
            "hash": hash_value,
            "hash_type": None,
            "cracked": False,
            "password": None,
            "method": None,
            "time_elapsed": 0,
            "attempts": 0
        }

        import time
        start_time = time.time()

        # Detect hash type
        detected_type = self.analyzer.detect_hash_type(hash_value)
        if not detected_type:
            result["error"] = "Unable to detect hash type"
            return result

        result["hash_type"] = detected_type
        self.logger.info(f"Detected hash type: {detected_type.upper()}")

        # Step 1: Common passwords
        self.logger.info("Checking common passwords...")
        for password in self.common_passwords:
            result["attempts"] += 1
            try:
                if self.hasher.hash_string(password, detected_type) == hash_value:
                    result.update({
                        "cracked": True,
                        "password": password,
                        "method": "Common Passwords",
                        "time_elapsed": time.time() - start_time
                    })
                    self.session_manager.add_result(
                        "dehash", result, sensitive=True)
                    return result
            except Exception as e:
                self.logger.debug(f"Error testing common password: {e}")

        # Step 2: Online lookup (HIBP)
        if use_online and detected_type == "sha1":
            self.logger.info("Attempting online HIBP lookup...")
            hibp_count = self.hibp_client.check_password(hash_value)
            if hibp_count > 0:
                result.update({
                    "cracked": True,
                    "password": f"[Found in {hibp_count} breaches via HIBP]",
                    "method": "Have I Been Pwned Database",
                    "time_elapsed": time.time() - start_time
                })
                self.session_manager.add_result(
                    "dehash", result, sensitive=True)
                return result

        # Step 3: Dictionary attack
        if wordlist_path:
            self.logger.info(f"Dictionary attack using: {wordlist_path}")
            dict_result = self.cracker.dictionary_attack(
                target=hash_value,
                wordlist_path=wordlist_path,
                hash_type=detected_type,
                max_words=max_words,
                apply_rules=True
            )
            if dict_result.get("found"):
                result.update({
                    "cracked": True,
                    "password": dict_result["password"],
                    "method": f"Dictionary Attack",
                    "time_elapsed": time.time() - start_time,
                    "attempts": result["attempts"] + dict_result.get("attempts", 0)
                })
                self.session_manager.add_result(
                    "dehash", result, sensitive=True)
                return result
            result["attempts"] += dict_result.get("attempts", 0)

        # Step 4: Hybrid attack if requested
        if strategy == "auto" or strategy == "hybrid":
            # Use hybrid attack directly instead of through execute_attack
            hybrid_result = self.cracker.hybrid_attack(
                target=hash_value,
                wordlist=self.common_passwords,
                hash_type=detected_type,
                append_charset="0123456789",
                max_append_length=3
            )
            if hybrid_result.get("found"):
                result.update({
                    "cracked": True,
                    "password": hybrid_result["password"],
                    "method": "Hybrid Attack",
                    "time_elapsed": time.time() - start_time,
                    "attempts": result["attempts"] + hybrid_result.get("attempts", 0)
                })
                self.session_manager.add_result(
                    "dehash", result, sensitive=True)
                return result
            result["attempts"] += hybrid_result.get("attempts", 0)

        result["time_elapsed"] = time.time() - start_time
        result["method"] = "All methods exhausted"
        self.session_manager.add_result("dehash", result, sensitive=True)

        return result

    # Add other methods from original PasswordAuditor class...
    def dictionary_attack(self, target: str, wordlist_path: str, **kwargs) -> Dict[str, Any]:
        """Perform dictionary attack."""
        result = self.cracker.dictionary_attack(
            target, wordlist_path, **kwargs)
        self.session_manager.add_result("dict", result, sensitive=True)
        return result

    def estimate_bruteforce(self, password: str, speed: int = 1000000) -> Dict[str, Any]:
        """Estimate brute-force time."""
        result = self.analyzer.estimate_bruteforce(password, speed)
        self.session_manager.add_result(
            "brute-estimate", result, sensitive=True)
        return result

    def generate_report(self, format: str = "text") -> str:
        """Generate security assessment report."""
        # Implementation from original code would go here
        return f"Report in {format} format (implementation needed)"

    def save_session(self, path: str = None) -> bool:
        """Save session to file."""
        return self.session_manager.save(path)

    def load_session(self, path: str) -> bool:
        """Load session from file."""
        return self.session_manager.load(path)
