"""Core library management modules.

This module provides:
- Catalog management (save, load, rebuild)
- Index generation for navigation
- Library operations
"""

from resourcelibrarian.core.catalog_manager import CatalogManager
from resourcelibrarian.core.index_generator import IndexGenerator

__all__ = [
    "CatalogManager",
    "IndexGenerator",
]
