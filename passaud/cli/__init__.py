"""
Command-line interface for PassAud.
"""

from .main import main
from .parser import create_parser
from .shell import PassAudShell

__all__ = ['main', 'create_parser', 'PassAudShell']