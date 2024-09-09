import os
import pytest

test_target = os.getenv("PYTHON_TEST_TARGET", "src")

if test_target == "pydantic_tfl_api":
    # from pydantic_tfl_api.models import ApiError, ResponseModel
    import models
    from pydantic_tfl_api.models import Line, LineArray
    from pydantic_tfl_api.endpoints import LineClient
    # from pydantic_tfl_api import client
else:
    pass

@pytest.mark.pydantic_tfl_api_only
@pytest.mark.skipif(test_target != "pydantic_tfl_api", reason="This test is only for pydantic_tfl_api")
def test_get_line_status_by_mode_rejected_with_invalid_api_key():
    api_token = "your_app_key"
    client = LineClient(api_token)
    assert client.client.app_key["app_key"] == api_token
    # should get a 429 error inside an ApiError object
    result = client.statusbymodebypathmodesquerydetailqueryseveritylevel(
        "overground,tube"
    )
    assert isinstance(result, models.ApiError)
    assert result.http_status_code == 429
    assert result.http_status == "Invalid App Key"


@pytest.mark.pydantic_tfl_api_only
@pytest.mark.skipif(test_target != "pydantic_tfl_api", reason="This test is only for pydantic_tfl_api")
def test_get_line_status_by_mode():
    # this API doesnt need authentication so we can use it to test that the API is working
    test_client = LineClient()
    # should get a list of Line objects
    result = test_client.statusbymodebypathmodesquerydetailqueryseveritylevel(
        "overground,tube"
    )
    assert isinstance(result, models.ResponseModel)
    response_content = result.content
    assert isinstance(response_content, LineArray)
    assert hasattr(response_content, "root")
    assert len(response_content.root) > 0
    # check that each item in the list is a Line object
    for item in response_content.root:
        assert isinstance(item, Line)
