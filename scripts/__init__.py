"""
Scripts for building Pydantic models from TfL OpenAPI specifications.

This module contains:
- fetch_tfl_specs.py: Fetches OpenAPI specifications from TfL API portal
- build_models.py: Generates Pydantic models from OpenAPI specs
- mappings.py: Contains TfL-specific entity name mappings
"""

__all__ = ["fetch_tfl_specs", "build_models", "mappings"]