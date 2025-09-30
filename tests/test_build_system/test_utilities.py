"""Tests for utilities module focusing on regression prevention."""

import pytest

from scripts.build_system.utilities import clean_enum_name, sanitize_field_name, sanitize_name


class TestSanitizeName:
    """Test sanitize_name function with focus on regression prevention."""

    def test_spaces_converted_to_camelcase(self) -> None:
        """REGRESSION: Ensure spaces are converted to CamelCase, not preserved."""
        # This test prevents the "Lift DisruptionsClient.py" bug
        assert sanitize_name("Lift Disruptions") == "LiftDisruptions"
        assert sanitize_name("Air Quality") == "AirQuality"
        assert sanitize_name("Bike Point") == "BikePoint"

    def test_single_word_capitalization(self) -> None:
        """Test single word capitalization."""
        assert sanitize_name("line") == "Line"
        assert sanitize_name("mode") == "Mode"
        assert sanitize_name("journey") == "Journey"

    def test_multiple_spaces_handled(self) -> None:
        """Test handling of multiple spaces."""
        assert sanitize_name("  Multiple   Spaces  ") == "MultipleSpaces"

    def test_mixed_case_preservation_with_spaces(self) -> None:
        """Test that mixed case is converted to standard CamelCase."""
        # The function uses .capitalize() which is the standard behavior
        assert sanitize_name("XML API") == "XmlApi"
        assert sanitize_name("HTTP Client") == "HttpClient"

    def test_underscore_and_space_combination(self) -> None:
        """Test combination of underscores and spaces."""
        # Function processes spaces first, then takes last part after underscore split
        # "user_profile data" -> "User_profileData" -> "profileData"
        assert sanitize_name("user_profile data") == "profileData"

    def test_no_spaces_in_output(self) -> None:
        """CRITICAL: Ensure no spaces ever appear in output (prevents invalid filenames)."""
        test_inputs = [
            "Lift Disruptions",
            "Air Quality Data",
            "Multi Word Test Case",
            "  Leading   Trailing  ",
            "Single",
            "two words",
            "THREE WORD CASE",
        ]

        for input_name in test_inputs:
            result = sanitize_name(input_name)
            assert " " not in result, f"Output '{result}' contains spaces for input '{input_name}'"
            assert result.replace("_", "").isalnum(), f"Output '{result}' contains invalid characters"

    def test_python_keywords_with_spaces(self) -> None:
        """Test Python keywords combined with spaces."""
        # After CamelCase conversion, these are no longer keywords
        assert sanitize_name("class data") == "ClassData"
        assert sanitize_name("def function") == "DefFunction"

    def test_digits_with_spaces(self) -> None:
        """Test handling of digits with spaces."""
        assert sanitize_name("123 test") == "Model_123Test"


class TestSanitizeFieldName:
    """Test field name sanitization."""

    def test_keywords_get_suffix(self) -> None:
        """Test that Python keywords get _field suffix."""
        assert sanitize_field_name("from") == "from_field"
        assert sanitize_field_name("class") == "class_field"
        assert sanitize_field_name("def") == "def_field"

    def test_non_keywords_unchanged(self) -> None:
        """Test that non-keywords remain unchanged."""
        assert sanitize_field_name("name") == "name"
        assert sanitize_field_name("value") == "value"
        assert sanitize_field_name("data") == "data"


class TestCleanEnumName:
    """Test enum name cleaning."""

    def test_special_characters_replaced(self) -> None:
        """Test special characters are replaced with underscores."""
        assert clean_enum_name("test-value") == "TEST_VALUE"
        assert clean_enum_name("test.value") == "TEST_VALUE"
        assert clean_enum_name("test value") == "TEST_VALUE"

    def test_leading_digits_handled(self) -> None:
        """Test leading digits get underscore prefix."""
        assert clean_enum_name("123test") == "_123TEST"

    def test_uppercase_conversion(self) -> None:
        """Test conversion to uppercase."""
        assert clean_enum_name("lowercase") == "LOWERCASE"
        assert clean_enum_name("MixedCase") == "MIXEDCASE"

    def test_trailing_underscore_removed(self) -> None:
        """REGRESSION: Test that trailing underscores are removed from enum names."""
        # This prevents the "PLANNED___SUBJECT_TO_FEASIBILITY_AND_CONSULTATION_" bug
        assert (
            clean_enum_name("Planned - Subject to feasibility and consultation.")
            == "PLANNED___SUBJECT_TO_FEASIBILITY_AND_CONSULTATION"
        )
        assert clean_enum_name("test value.") == "TEST_VALUE"
        assert clean_enum_name("trailing dot...") == "TRAILING_DOT"

    def test_leading_underscore_preserved_for_digits(self) -> None:
        """Test that leading underscores are preserved when added for digit prefixes."""
        result = clean_enum_name("123test")
        assert result == "_123TEST"
        assert result[0] == "_"  # Leading underscore preserved


class TestRegressionPrevention:
    """Specific regression tests for known issues."""

    @pytest.mark.parametrize(
        "input_name,expected",
        [
            ("Lift Disruptions", "LiftDisruptions"),
            ("Air Quality", "AirQuality"),
            ("Bike Point", "BikePoint"),
            ("Stop Point", "StopPoint"),
            ("Road Disruptions", "RoadDisruptions"),
            ("Vehicle Match", "VehicleMatch"),
            ("Search Response", "SearchResponse"),
        ],
    )
    def test_known_problematic_api_names(self, input_name: str, expected: str) -> None:
        """Test specific API names that have caused issues."""
        result = sanitize_name(input_name)
        assert result == expected
        assert " " not in result  # Critical: no spaces

    def test_filename_validity(self) -> None:
        """Test that generated names are valid Python filenames."""
        problematic_names = [
            "Lift Disruptions",
            "Multi Word API Name",
            "  Spaces  Everywhere  ",
            "special-chars & symbols",
        ]

        for name in problematic_names:
            result = sanitize_name(name)
            # Must be valid Python identifier
            assert result.isidentifier(), f"'{result}' is not a valid Python identifier"
            # Must not contain spaces (invalid for filenames)
            assert " " not in result, f"'{result}' contains spaces"
