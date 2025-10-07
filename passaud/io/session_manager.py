"""
Session management for PassAud.
"""

import json
import logging
import os
import tempfile
import base64
import secrets
from datetime import datetime
from typing import Dict, Any
import ctypes

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

logger = logging.getLogger(__name__)


class SessionManager:
    """Manage session data with encryption."""

    def __init__(self, config_manager=None, user_password=None):
        self.config_manager = config_manager
        self.session_key = self._generate_session_key(user_password)
        self.session_data = {
            "timestamp": datetime.now().isoformat(),
            "commands": [],
            "results": []
        }
        self.session_id = secrets.token_hex(16)
        self.logger = logging.getLogger(__name__)

    def _generate_session_key(self, user_password=None) -> bytes:
        """Generate a secure session key."""
        key_file = self.config_manager.get('DEFAULT', 'session_key_file',
                                           default=os.path.expanduser("~/.passaud_session.key"))

        if user_password:
            salt = secrets.token_bytes(16)
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(user_password.encode()))
            return key

        if os.path.exists(key_file):
            try:
                with open(key_file, 'rb') as f:
                    return f.read()
            except Exception:
                pass

        key = secrets.token_bytes(32)

        try:
            os.makedirs(os.path.dirname(key_file), exist_ok=True)
            with open(key_file, 'wb') as f:
                f.write(key)
            return key
        except Exception as e:
            self.logger.warning(f"Could not save session key: {e}")
            return key

    def _encrypt_data(self, data: Any) -> str:
        """Encrypt session data using AES."""
        try:
            json_data = json.dumps(data)
            f = Fernet(self.session_key)
            encrypted = f.encrypt(json_data.encode('utf-8'))
            return base64.b64encode(encrypted).decode('utf-8')
        except Exception as e:
            self.logger.error(f"Encryption failed: {e}")
            raise

    def _decrypt_data(self, encrypted_data: str) -> Any:
        """Decrypt session data using AES."""
        try:
            encrypted = base64.b64decode(encrypted_data)
            f = Fernet(self.session_key)
            decrypted = f.decrypt(encrypted)
            return json.loads(decrypted.decode('utf-8'))
        except Exception as e:
            self.logger.error(f"Decryption failed: {e}")
            raise

    def add_result(self, command: str, data: Dict[str, Any], sensitive: bool = False) -> None:
        """Add a result to session data."""
        if sensitive:
            sanitized_data = {k: ('***REDACTED***' if k in ['password', 'hash', 'target'] else v)
                              for k, v in data.items()}
            self.session_data["results"].append({
                "command": command,
                "result": sanitized_data,
                "sensitive": True
            })
        else:
            self.session_data["results"].append({
                "command": command,
                "result": data,
                "sensitive": False
            })

    def save(self, path: str = None) -> bool:
        """Save encrypted session to file."""
        try:
            if not path:
                path = f"passaud_session_{self.session_id}_{int(datetime.now().timestamp())}.enc"

            encrypted_data = self._encrypt_data(self.session_data)
            with open(path, 'w') as f:
                f.write(encrypted_data)
            self.logger.info(f"Session saved to {path}")
            return True
        except Exception as e:
            self.logger.error(f"Error saving session: {e}")
            return False

    def load(self, path: str) -> bool:
        """Load encrypted session from file."""
        try:
            if not self._validate_file_path(path):
                self.logger.error(f"Invalid file path: {path}")
                return False

            with open(path, 'r') as f:
                encrypted_data = f.read()
            self.session_data = self._decrypt_data(encrypted_data)
            self.logger.info(f"Session loaded from {path}")
            return True
        except Exception as e:
            self.logger.error(f"Error loading session: {e}")
            return False

    def _validate_file_path(self, path: str) -> bool:
        """Validate file path to prevent directory traversal."""
        try:
            abs_path = os.path.abspath(path)
            allowed_dirs = [
                os.path.abspath("."),
                os.path.expanduser("~"),
                tempfile.gettempdir()
            ]

            for allowed_dir in allowed_dirs:
                if abs_path.startswith(allowed_dir):
                    return True

            self.logger.warning(
                f"File path not in allowed directories: {path}")
            return False
        except Exception as e:
            self.logger.error(f"Path validation error: {e}")
            return False

    def clear_sensitive_data(self):
        """Securely clear sensitive data from memory."""
        if hasattr(self, 'session_key') and self.session_key:
            ctypes.memset(ctypes.addressof(ctypes.c_char.from_buffer(
                self.session_key)), 0, len(self.session_key))

        self.session_data = {
            "timestamp": datetime.now().isoformat(),
            "commands": [],
            "results": []
        }
