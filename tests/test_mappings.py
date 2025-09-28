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

    def _get_all_mapping_data(self):
        """Helper to extract all mapping data for parameterized tests."""
        from mappings import tfl_mappings

        # Extract all api mappings for testing
        api_data = []
        mapping_data = []

        for api_name, mapping in tfl_mappings.items():
            api_data.append((api_name, mapping))
            # Only add non-empty mappings to avoid conditional logic
            if mapping:
                for old_name, new_name in mapping.items():
                    mapping_data.append((api_name, old_name, new_name))

        return api_data, mapping_data

    @pytest.mark.parametrize("api_name,mapping", _get_all_mapping_data(None)[0])
    def test_mapping_is_dictionary(self, api_name, mapping):
        """Test that each API mapping is a dictionary."""
        assert isinstance(mapping, dict), f"Mapping for {api_name} should be a dictionary"

    @pytest.mark.parametrize("api_name,old_name,new_name", _get_all_mapping_data(None)[1])
    def test_mapping_values_are_strings(self, api_name, old_name, new_name):
        """Test that mapping keys and values are strings."""
        assert isinstance(old_name, str), f"Mapping key should be string in {api_name}"
        assert isinstance(new_name, str), f"Mapping value should be string in {api_name}"

    @pytest.mark.parametrize("api_name,old_name,new_name", _get_all_mapping_data(None)[1])
    def test_mapping_names_are_non_empty(self, api_name, old_name, new_name):
        """Test that mapping keys and values are non-empty."""
        assert old_name.strip(), f"Empty old name found in {api_name}"
        assert new_name.strip(), f"Empty new name found in {api_name}"

    @pytest.mark.parametrize("api_name,old_name,expected_new_name", [
        ("AirQuality", "System.Object", "Tfl.Api.Presentation.Entities.LondonAirForecast"),
    ])
    def test_specific_mappings(self, api_name, old_name, expected_new_name):
        """Test specific known mappings using parameterization."""
        from mappings import tfl_mappings

        assert api_name in tfl_mappings, f"Expected API '{api_name}' not found in mappings"
        mapping = tfl_mappings[api_name]
        assert old_name in mapping, f"Expected old name '{old_name}' not found in mapping for API '{api_name}'"
        assert mapping[old_name] == expected_new_name, (
            f"Expected new name '{expected_new_name}' for old name '{old_name}' in API '{api_name}', "
            f"but got '{mapping[old_name]}'"
        )

    def test_bikepoint_has_place_array_mappings(self):
        """Test that BikePoint has PlaceArray mappings."""
        from mappings import tfl_mappings

        # This is a specific structural test that doesn't need parameterization
        assert "BikePoint" in tfl_mappings, "BikePoint should exist in mappings"
        bike_point = tfl_mappings["BikePoint"]
        place_array_mappings = [k for k in bike_point.keys() if "PlaceArray" in k]
        assert len(place_array_mappings) > 0, "BikePoint should have PlaceArray mappings"