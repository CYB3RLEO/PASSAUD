"""
Strategy registry for PassAud.
"""
from .base import AttackStrategy
from .dictionary import DictionaryAttackStrategy
from .brute_force import BruteForceAttackStrategy
from .hybrid import HybridAttackStrategy
from .mask import MaskAttackStrategy

# Registry of available strategies
STRATEGY_REGISTRY = {
    'dictionary': DictionaryAttackStrategy,
    'brute_force': BruteForceAttackStrategy,
    'hybrid': HybridAttackStrategy,
    'mask': MaskAttackStrategy
}

__all__ = [
    'AttackStrategy',
    'DictionaryAttackStrategy', 
    'BruteForceAttackStrategy',
    'HybridAttackStrategy',
    'MaskAttackStrategy',
    'STRATEGY_REGISTRY'
]