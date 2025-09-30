"""
Backward compatibility tests for TfL mappings.

These tests ensure the mapping loader provides the expected interface
for existing code that depends on the legacy mappings format.
"""


class TestMappingsBackwardCompatibility:
    """Test backward compatibility of the new mapping system."""

    def test_load_tfl_mappings_function_exists(self) -> None:
        """Test that the load_tfl_mappings function can be imported."""
        from scripts.mapping_loader import load_tfl_mappings

        assert callable(load_tfl_mappings)

    def test_legacy_format_structure(self) -> None:
        """Test that the legacy format maintains expected structure."""
        from scripts.mapping_loader import load_tfl_mappings

        tfl_mappings = load_tfl_mappings()

        # Should be a dictionary
        assert isinstance(tfl_mappings, dict)

        # Should have expected APIs
        expected_apis = [
            "AccidentStats",
            "AirQuality",
            "BikePoint",
            "Journey",
            "Line",
            "Mode",
            "Place",
            "Road",
            "Search",
            "StopPoint",
            "Vehicle",
        ]

        # Validate all expected APIs exist
        missing_apis = [api for api in expected_apis if api not in tfl_mappings]
        assert not missing_apis, f"Expected APIs not found: {missing_apis}"

        # Validate all expected APIs are dictionaries
        non_dict_apis = [api for api in expected_apis if not isinstance(tfl_mappings[api], dict)]
        assert not non_dict_apis, f"APIs should be dicts but aren't: {non_dict_apis}"

    def test_build_models_compatibility(self) -> None:
        """Test that build_models.py can still import and use mappings."""
        # This would be the typical usage in build_models.py
        from scripts.mapping_loader import load_tfl_mappings

        tfl_mappings = load_tfl_mappings()

        # Test typical usage patterns
        assert "Line" in tfl_mappings
        line_mappings = tfl_mappings["Line"]
        assert isinstance(line_mappings, dict)
        assert len(line_mappings) > 0

        # All values should be strings
        non_string_keys = [k for k in line_mappings if not isinstance(k, str)]
        assert not non_string_keys, f"Non-string keys found: {non_string_keys}"

        non_string_values = [v for v in line_mappings.values() if not isinstance(v, str)]
        assert not non_string_values, f"Non-string values found: {non_string_values}"

        empty_keys = [k for k in line_mappings if len(k.strip()) == 0]
        assert not empty_keys, f"Empty keys found: {empty_keys}"

        empty_values = [v for v in line_mappings.values() if len(v.strip()) == 0]
        assert not empty_values, f"Empty values found: {empty_values}"

    def test_mapping_loader_api_methods(self) -> None:
        """Test that the MappingLoader class provides expected API methods."""
        from scripts.mapping_loader import MappingLoader

        loader = MappingLoader()

        # Test basic methods exist and work
        apis = loader.list_apis()
        assert isinstance(apis, list)
        assert "Line" in apis

        line_mappings = loader.get_api_mappings("Line")
        assert isinstance(line_mappings, dict)

        metadata = loader.get_metadata()
        assert isinstance(metadata, dict)
        assert "version" in metadata
        assert "last_updated" in metadata
        assert "source" in metadata

    def test_validation_works(self) -> None:
        """Test that schema validation is functional."""
        from scripts.mapping_loader import MappingLoader

        loader = MappingLoader()

        # Should not raise an exception
        assert loader.validate() is True
