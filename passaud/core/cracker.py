"""
Core password cracking functionality.
"""

import logging
import multiprocessing as mp
import time
import itertools
import string
from typing import Optional, List, Dict, Any, Generator
from abc import ABC, abstractmethod
from tqdm import tqdm

from passaud.config.config_manager import ConfigManager
from passaud.core.rule_engine import RuleEngine
from passaud.external.gpu_accelerator import GPUAccelerator
from passaud.utils.helpers import chunk_list

logger = logging.getLogger(__name__)


class AttackStrategy(ABC):
    """Abstract base class for attack strategies."""

    @abstractmethod
    def execute(self, target: str, **kwargs) -> Dict[str, Any]:
        """Execute the attack strategy."""
        pass

    @abstractmethod
    def get_name(self) -> str:
        """Get the name of the strategy."""
        pass


class Cracker:
    """Main password cracking class."""

    def __init__(self, config_manager: ConfigManager = None):
        self.config_manager = config_manager or ConfigManager()
        self.rule_engine = RuleEngine(config_manager)
        self.gpu_accelerator = GPUAccelerator()

        # Initialize strategies
        self.strategies: Dict[str, AttackStrategy] = {}
        self._initialize_strategies()

        self.logger = logging.getLogger(__name__)
        self.batch_size = self.config_manager.get_int(
            'DEFAULT', 'batch_size', 1000)

    def _initialize_strategies(self):
        """Initialize all attack strategies."""
        from passaud.core.strategies import (
            DictionaryAttackStrategy, BruteForceAttackStrategy,
            HybridAttackStrategy, MaskAttackStrategy
        )

        self.strategies = {
            'dictionary': DictionaryAttackStrategy(self, self.rule_engine),
            'brute_force': BruteForceAttackStrategy(self),
            'hybrid': HybridAttackStrategy(self, self.rule_engine),
            'mask': MaskAttackStrategy(self)
        }

    def register_strategy(self, name: str, strategy: AttackStrategy) -> None:
        """Register a new attack strategy."""
        self.strategies[name] = strategy
        self.logger.info(f"Registered attack strategy: {name}")

    def execute_attack(self, strategy_name: str, target: str, **kwargs) -> Dict[str, Any]:
        """Execute a specific attack strategy."""
        if strategy_name not in self.strategies:
            raise ValueError(f"Unknown attack strategy: {strategy_name}")

        self.logger.info(f"Executing {strategy_name} attack on target")
        return self.strategies[strategy_name].execute(target, **kwargs)

    def dictionary_attack(self, target: str, wordlist_path: str, hash_type: str = None,
                          apply_rules: bool = False, max_variations: int = 100,
                          threads: int = None, batch_size: int = 1000,
                          # ADDED max_words
                          max_words: int = None) -> Dict[str, Any]:
        """Perform dictionary attack with multiprocessing support."""

        results = {
            'found': False,
            'password': None,
            'attempts': 0,
            'time_elapsed': 0
        }

        start_time = time.time()

        # Determine number of threads
        if threads is None:
            threads = self.config_manager.get_int(
                'DEFAULT', 'max_threads', mp.cpu_count())

        # Load wordlist from path
        from passaud.io.wordlist_loader import WordlistLoader
        loader = WordlistLoader()
        wordlist = list(loader.stream_wordlist(
            wordlist_path, max_words=max_words))
        total_words = len(wordlist)

        # Create progress bar
        pbar = tqdm(
            total=total_words,
            desc="Dictionary attack",
            unit="words",
            disable=total_words < 1000
        )

        # Process in batches
        for i in range(0, len(wordlist), batch_size):
            batch = wordlist[i:i + batch_size]
            found = self._process_batch(batch, target, hash_type, apply_rules,
                                        max_variations, results, pbar, threads)
            if found:
                pbar.close()
                results['time_elapsed'] = time.time() - start_time
                return results

        pbar.close()
        results['time_elapsed'] = time.time() - start_time
        return results

    def _process_batch(self, batch, target, hash_type, apply_rules, max_variations, results, pbar, threads):
        """Process a batch of words."""
        for word in batch:
            result = self._test_word(
                word, target, hash_type, apply_rules, max_variations)
            results['attempts'] += result['attempts']
            pbar.update(1)

            if result['found']:
                results['found'] = True
                results['password'] = result['password']
                return True
        return False

    def _test_word(self, word, target, hash_type, apply_rules, max_variations):
        """Test a single word against the target."""
        result = {
            'found': False,
            'password': None,
            'attempts': 0
        }

        # Apply rules if requested
        test_words = [word]
        if apply_rules:
            test_words = self.rule_engine.apply_rules(word, max_variations)

        for test_word in test_words:
            result['attempts'] += 1
            try:
                if hash_type:
                    hashed = self.hash_string(test_word, hash_type)
                    if hashed == target:
                        result.update({
                            'found': True,
                            'password': test_word
                        })
                        return result
                elif test_word == target:
                    result.update({
                        'found': True,
                        'password': test_word
                    })
                    return result
            except Exception as e:
                logger.debug(f"Error testing {test_word}: {e}")
                continue

        return result

    def brute_force_attack(self, hash_value: str, hash_type: str, max_length: int = 8,
                           charset: str = None, threads: int = None) -> Dict[str, Any]:
        """Perform brute-force attack."""
        if charset is None:
            charset = string.ascii_lowercase + string.digits

        results = {
            'found': False,
            'password': None,
            'attempts': 0,
            'time_elapsed': 0
        }

        start_time = time.time()

        # Try different lengths
        for length in range(1, max_length + 1):
            for candidate in itertools.product(charset, repeat=length):
                candidate_str = ''.join(candidate)
                results['attempts'] += 1

                try:
                    hashed_candidate = self.hash_string(
                        candidate_str, hash_type)
                    if hashed_candidate == hash_value:
                        results.update({
                            'found': True,
                            'password': candidate_str,
                            'time_elapsed': time.time() - start_time
                        })
                        return results
                except Exception as e:
                    logger.debug(f"Error testing {candidate_str}: {e}")
                    continue

        results['time_elapsed'] = time.time() - start_time
        return results

    def hybrid_attack(self, target: str, wordlist, hash_type: str = None,
                      append_charset: str = None, max_append_length: int = 3,
                      threads: int = None) -> Dict[str, Any]:
        """Perform hybrid attack."""
        if append_charset is None:
            append_charset = string.digits

        results = {
            'found': False,
            'password': None,
            'attempts': 0,
            'time_elapsed': 0
        }

        start_time = time.time()

        words = list(wordlist) if not isinstance(
            wordlist, str) else self._stream_wordlist(wordlist)

        for word in words:
            results['attempts'] += 1
            try:
                if hash_type:
                    hashed = self.hash_string(word, hash_type)
                    if hashed == target:
                        results.update({
                            'found': True,
                            'password': word,
                            'time_elapsed': time.time() - start_time
                        })
                        return results
                elif word == target:
                    results.update({
                        'found': True,
                        'password': word,
                        'time_elapsed': time.time() - start_time
                    })
                    return results
            except Exception as e:
                logger.debug(f"Error testing {word}: {e}")
                continue

            # Try with appended characters
            for length in range(1, max_append_length + 1):
                for append_chars in itertools.product(append_charset, repeat=length):
                    candidate = word + ''.join(append_chars)
                    results['attempts'] += 1

                    try:
                        if hash_type:
                            hashed = self.hash_string(candidate, hash_type)
                            if hashed == target:
                                results.update({
                                    'found': True,
                                    'password': candidate,
                                    'time_elapsed': time.time() - start_time
                                })
                                return results
                        elif candidate == target:
                            results.update({
                                'found': True,
                                'password': candidate,
                                'time_elapsed': time.time() - start_time
                            })
                            return results
                    except Exception as e:
                        logger.debug(f"Error testing {candidate}: {e}")
                        continue

        results['time_elapsed'] = time.time() - start_time
        return results

    def mask_attack(self, target: str, hash_type: str, mask_pattern: str,
                    threads: int = None) -> Dict[str, Any]:
        """Perform mask attack."""
        results = {
            'found': False,
            'password': None,
            'attempts': 0,
            'time_elapsed': 0
        }

        start_time = time.time()

        # Parse mask pattern
        charset_map = {
            '?l': string.ascii_lowercase,
            '?u': string.ascii_uppercase,
            '?d': string.digits,
            '?s': string.punctuation,
            '?a': string.ascii_letters + string.digits + string.punctuation
        }

        # Split pattern into components
        pattern_parts = []
        i = 0
        while i < len(mask_pattern):
            if i + 1 < len(mask_pattern) and mask_pattern[i] == '?' and mask_pattern[i+1] in 'ludsah':
                pattern_parts.append(mask_pattern[i:i+2])
                i += 2
            else:
                pattern_parts.append(mask_pattern[i])
                i += 1

        # Generate candidates based on pattern
        charsets = [charset_map.get(part, part) for part in pattern_parts]

        for candidate in itertools.product(*charsets):
            candidate_str = ''.join(candidate)
            results['attempts'] += 1

            try:
                if hash_type:
                    hashed = self.hash_string(candidate_str, hash_type)
                    if hashed == target:
                        results.update({
                            'found': True,
                            'password': candidate_str,
                            'time_elapsed': time.time() - start_time
                        })
                        return results
                elif candidate_str == target:
                    results.update({
                        'found': True,
                        'password': candidate_str,
                        'time_elapsed': time.time() - start_time
                    })
                    return results
            except Exception as e:
                logger.debug(f"Error testing {candidate_str}: {e}")
                continue

        results['time_elapsed'] = time.time() - start_time
        return results

    def hash_string(self, input_str: str, algorithm: str = "md5") -> str:
        """Generate hash for a string."""
        import hashlib
        import bcrypt
        import argon2
        import scrypt

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
            salt = b'salt_16_bytes_'  # In production, use os.urandom(16)
            hashed = scrypt.hash(input_str.encode(), salt, N=16384, r=8, p=1)
            return hashed.hex()
        elif algorithm == "argon2":
            hasher = argon2.PasswordHasher()
            return hasher.hash(input_str)
        else:
            raise ValueError(f"Unsupported algorithm: {algorithm}")

    def _stream_wordlist(self, file_path: str) -> Generator[str, None, None]:
        """Stream words from a wordlist file."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    word = line.strip()
                    if word:
                        yield word
        except Exception as e:
            logger.error(f"Error reading wordlist: {e}")
            raise
