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

    def test_known_apis_exist(self):
        """Test that expected APIs have mappings."""
        from mappings import tfl_mappings

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
            "Vehicle"
        ]

        for api in expected_apis:
            assert api in tfl_mappings, f"Expected API '{api}' not found in mappings"

    def test_mapping_structure(self):
        """Test the structure of individual API mappings."""
        from mappings import tfl_mappings

        for api_name, mapping in tfl_mappings.items():
            assert isinstance(mapping, dict), f"Mapping for {api_name} should be a dictionary"

            # Some APIs may have empty mappings (like 'crowding'), which is valid
            if len(mapping) > 0:
                # Check that all keys and values are strings
                for old_name, new_name in mapping.items():
                    assert isinstance(old_name, str), f"Mapping key should be string in {api_name}"
                    assert isinstance(new_name, str), f"Mapping value should be string in {api_name}"

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