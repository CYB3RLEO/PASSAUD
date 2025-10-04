"""
Base strategy class for all attack strategies.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any

class AttackStrategy(ABC):
    """Abstract base class that all attack strategies must implement."""
    
    @abstractmethod
    def execute(self, target: str, **kwargs) -> Dict[str, Any]:
        """Execute the attack strategy on the target."""
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Return the name of the strategy."""
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """Return a description of the strategy."""
        pass