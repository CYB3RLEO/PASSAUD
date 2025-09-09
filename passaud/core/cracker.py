"""
Core password cracking functionality.
"""

import logging
from typing import Optional, List, Dict, Any
from abc import ABC, abstractmethod

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
    
    def __init__(self):
        self.strategies: Dict[str, AttackStrategy] = {}
        self.logger = logging.getLogger(__name__)
    
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