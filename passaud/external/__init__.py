"""
External integrations for PassAud.
"""

from .hibp_client import HIBPClient
from .gpu_accelerator import GPUAccelerator

__all__ = ['HIBPClient', 'GPUAccelerator']