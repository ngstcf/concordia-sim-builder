"""
Custom prefabs for Concordia simulations.

This module contains custom entity and game master prefabs that extend
the base Concordia functionality.
"""

from backend.prefabs import context_aware_scripted
from backend.prefabs import nested_simulation
from backend.prefabs import grounded_variables

__all__ = ['context_aware_scripted', 'nested_simulation', 'grounded_variables']
