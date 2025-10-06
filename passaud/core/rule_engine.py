"""
Rule engine for password transformations.
"""

import logging
import re
import string
import itertools
from typing import List, Dict, Any, Callable
from datetime import datetime

logger = logging.getLogger(__name__)

class RuleEngine:
    """Advanced rule engine for password transformations."""
    
    def __init__(self, config_manager=None):
        self.config_manager = config_manager
        self.logger = logging.getLogger(__name__)
        self.rules = self._load_default_rules()
        self.custom_rules = self._load_custom_rules()
    
    def _load_default_rules(self) -> List[Dict[str, Any]]:
        """Load default transformation rules."""
        return [
            {"name": "no_change", "func": lambda x: [x]},
            {"name": "capitalize", "func": lambda x: [x.capitalize()]},
            {"name": "uppercase", "func": lambda x: [x.upper()]},
            {"name": "lowercase", "func": lambda x: [x.lower()]},
            {"name": "toggle_case", "func": lambda x: [x.swapcase()]},
            {"name": "leet_speak", "func": self._leet_transform},
            {"name": "append_digits", "func": self._append_digits},
            {"name": "prepend_digits", "func": self._prepend_digits},
            {"name": "reverse", "func": lambda x: [x[::-1]]},
            {"name": "duplicate", "func": lambda x: [x + x]},
            {"name": "reflect", "func": lambda x: [x + x[::-1]]},
            {"name": "year_suffix", "func": self._year_suffix},
            {"name": "common_suffix", "func": self._common_suffix},
        ]
    
    def _load_custom_rules(self) -> List[Dict[str, Any]]:
        """Load custom rules from configuration."""
        # TODO: Implement custom rule loading from config
        return []
    
    def _leet_transform(self, word: str, max_variations: int = 50) -> List[str]:
        """Apply leet speak transformations."""
        substitutions = {
            'a': ['4', '@'],
            'b': ['8'],
            'e': ['3'],
            'g': ['9'],
            'i': ['1', '!'],
            'l': ['1'],
            'o': ['0'],
            's': ['5', '$'],
            't': ['7'],
            'z': ['2']
        }
        
        results = [word]
        for i, char in enumerate(word.lower()):
            if char in substitutions and len(results) < max_variations:
                new_results = []
                for result in results:
                    for sub in substitutions[char]:
                        if len(new_results) >= max_variations:
                            break
                        new_results.append(result[:i] + sub + result[i+1:])
                results.extend(new_results)
                results = list(dict.fromkeys(results))
        
        return results[:max_variations]
    
    def _append_digits(self, word: str) -> List[str]:
        """Append digits to the word."""
        return [word + str(i) for i in range(0, 100)]
    
    def _prepend_digits(self, word: str) -> List[str]:
        """Prepend digits to the word."""
        return [str(i) + word for i in range(0, 100)]
    
    def _year_suffix(self, word: str) -> List[str]:
        """Append years to the word."""
        current_year = datetime.now().year
        years = [str(i) for i in range(current_year - 30, current_year + 5)]
        return [word + year for year in years]
    
    def _common_suffix(self, word: str) -> List[str]:
        """Append common suffixes to the word."""
        suffixes = ['!', '@', '#', '$', '%', '^', '&', '*', '?', '123', '!@#']
        return [word + suffix for suffix in suffixes]
    
    def apply_rules(self, word: str, max_variations: int = 100) -> List[str]:
        """Apply all rules to a word with limits to prevent combinatorial explosion."""
        variations = set([word])
        
        for rule in self.rules:
            if len(variations) >= max_variations:
                break
            try:
                new_variations = rule["func"](word)
                variations.update(new_variations)
            except Exception as e:
                self.logger.warning(f"Error applying rule {rule['name']}: {e}")
                continue
        
        for rule in self.custom_rules:
            if len(variations) >= max_variations:
                break
            try:
                new_variations = rule["func"](word)
                variations.update(new_variations)
            except Exception as e:
                self.logger.warning(f"Error applying custom rule {rule['name']}: {e}")
                continue
        
        return list(variations)[:max_variations]