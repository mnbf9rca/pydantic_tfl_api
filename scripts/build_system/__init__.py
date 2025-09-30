"""Refactored build system for pydantic-tfl-api.

This package contains a modular, object-oriented refactoring of the original
monolithic build_models.py script. Each class handles a specific aspect of
the build process:

- ModelBuilder: Creates Pydantic models from OpenAPI schemas
- DependencyResolver: Handles model dependencies and circular references
- FileManager: Manages all file I/O operations
- SpecProcessor: Loads and processes OpenAPI specifications
- ClientGenerator: Generates API client classes and configurations
- BuildCoordinator: Orchestrates the complete build workflow

The refactored system maintains full backward compatibility while providing
better testability, maintainability, and modularity.
"""

from .build_coordinator import BuildCoordinator
from .client_generator import ClientGenerator
from .dependency_resolver import DependencyResolver
from .file_manager import FileManager
from .model_builder import ModelBuilder
from .spec_processor import SpecProcessor

__all__ = [
    "BuildCoordinator",
    "ClientGenerator",
    "DependencyResolver",
    "FileManager",
    "ModelBuilder",
    "SpecProcessor",
]
