from pydantic_tfl_api import Client
from pydantic_tfl_api.models import ApiError, LineStatus, Line

# basically, we just want to do a minimal set of tests
# to make sure that the pydantic models load
# and that the TFL API connectivity is ok - although we'll have 
def test_create_client_with_api_token():
    # checks that the API key is being passed to the RestClient
    api_token = 'your_app_key'
    client = Client(api_token)
    assert client.client.app_key['app_key'] == api_token

def test_get_line_status_by_mode_rejected_with_invalid_api_key():
    api_token = 'your_app_key'
    client = Client(api_token)
    assert client.client.app_key['app_key'] == api_token
    # should get a 429 error inside an ApiError object
    result = client.get_line_status_by_mode('overground,tube')
    assert isinstance(result, ApiError)
    assert result.http_status_code == 429
    assert result.http_status == 'Invalid App Key'

def test_get_line_status_by_mode():
    # this API doesnt need authentication so we can use it to test that the API is working
    client = Client()
    # should get a list of Line objects
    result = client.get_line_status_by_mode('overground,tube')
    assert isinstance(result, list)
    assert len(result) > 0
    # check that each item in the list is a Line object
    for item in result:
        assert isinstance(item,Line)