"""
Tests for the mappings.py module.
"""
import os
import sys

import pytest

# Add scripts directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))


class TestTflMappings:
    """Test the TfL mappings configuration."""

    def test_mappings_import(self):
        """Test that mappings module imports successfully."""
        from mappings import tfl_mappings
        assert isinstance(tfl_mappings, dict)
        assert len(tfl_mappings) > 0

    @pytest.mark.parametrize("api_name", [
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
        "Vehicle"
    ])
    def test_known_apis_exist(self, api_name):
        """Test that expected APIs have mappings."""
        from mappings import tfl_mappings
        assert api_name in tfl_mappings, f"Expected API '{api_name}' not found in mappings"

    def test_all_mappings_are_dictionaries(self):
        """Test that all API mappings are dictionaries."""
        from mappings import tfl_mappings

        for api_name, mapping in tfl_mappings.items():
            assert isinstance(mapping, dict), f"Mapping for {api_name} should be a dictionary"

    def test_mapping_keys_and_values_are_strings(self):
        """Test that all mapping keys and values are strings."""
        from mappings import tfl_mappings

        for api_name, mapping in tfl_mappings.items():
            if len(mapping) > 0:  # Some APIs may have empty mappings (like 'crowding'), which is valid
                for old_name, new_name in mapping.items():
                    assert isinstance(old_name, str), f"Mapping key should be string in {api_name}"
                    assert isinstance(new_name, str), f"Mapping value should be string in {api_name}"

    def test_mapping_names_are_non_empty(self):
        """Test that mapping keys and values are non-empty."""
        from mappings import tfl_mappings

        for api_name, mapping in tfl_mappings.items():
            for old_name, new_name in mapping.items():
                assert old_name.strip(), f"Empty old name found in {api_name}"
                assert new_name.strip(), f"Empty new name found in {api_name}"

    def test_specific_mappings(self):
        """Test specific known mappings."""
        from mappings import tfl_mappings

        # Test AirQuality mapping
        if "AirQuality" in tfl_mappings:
            air_quality = tfl_mappings["AirQuality"]
            assert "System.Object" in air_quality
            assert air_quality["System.Object"] == "Tfl.Api.Presentation.Entities.LondonAirForecast"

        # Test that BikePoint has PlaceArray mappings
        if "BikePoint" in tfl_mappings:
            bike_point = tfl_mappings["BikePoint"]
            place_array_mappings = [k for k in bike_point.keys() if "PlaceArray" in k]
            assert len(place_array_mappings) > 0, "BikePoint should have PlaceArray mappings"