import pytest
from pydantic import BaseModel, ValidationError
from datetime import datetime, timedelta

from pydantic_tfl_api.client import Client

class TestModel(BaseModel):
    name: str
    age: int
    content_expires: datetime | None = None

@pytest.mark.parametrize(
    "Model, response_json, result_expiry, expected_name, expected_age, expected_expiry",
    [
        # Happy path tests
        (TestModel, {"name": "Alice", "age": 30}, datetime(2023, 12, 31), "Alice", 30, datetime(2023, 12, 31)),
        (TestModel, {"name": "Bob", "age": 25}, None, "Bob", 25, None),
        
        # Edge cases
        (TestModel, {"name": "", "age": 0}, datetime(2023, 12, 31), "", 0, datetime(2023, 12, 31)),
        (TestModel, {"name": "Charlie", "age": -1}, None, "Charlie", -1, None),
        
        # Error cases
        (TestModel, {"name": "Alice"}, datetime(2023, 12, 31), None, None, None),  # Missing age
        (TestModel, {"age": 30}, datetime(2023, 12, 31), None, None, None),  # Missing name
        (TestModel, {"name": "Alice", "age": "thirty"}, datetime(2023, 12, 31), None, None, None),  # Invalid age type
    ],
    ids=[
        "happy_path_with_expiry",
        "happy_path_without_expiry",
        "edge_case_empty_name_and_zero_age",
        "edge_case_negative_age",
        "error_case_missing_age",
        "error_case_missing_name",
        "error_case_invalid_age_type",
    ]
)
def test_create_model_with_expiry(Model, response_json, result_expiry, expected_name, expected_age, expected_expiry):
    
    # Act
    if expected_name is None:
        with pytest.raises(ValidationError):
            Client._create_model_with_expiry(None, Model, response_json, result_expiry)
    else:
        instance = Client._create_model_with_expiry(None, Model, response_json, result_expiry)
    
        # Assert
        assert instance.name == expected_name
        assert instance.age == expected_age
        assert instance.content_expires == expected_expiry
