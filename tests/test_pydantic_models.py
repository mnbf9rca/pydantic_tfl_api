# this suite tests that the pydantic models can deserialise the JSON responses from the TFL API
# it uses snapshot responses from the API on a day that there was some disruption etc.

from .config_for_tests import response_to_request_mapping
from requests.models import Response
import json
from pydantic import BaseModel
from typing import List

from pydantic_tfl_api import Client


# response_to_request_mapping contains a dict
# response_to_request_mapping = {
#     "stopPointsByLineId_victoria_None_StopPoint": {
#         "endpoint": "stopPointsByLineId",
#         "endpoint_args": ["victoria"],
#         "endpoint_params": {},
#         "model": "StopPoint",
#     },
#    ...

# so we need to create a paramaterised test
# for each key in response_to_request_mapping
# the key is both the name of the test, and a json file containing a serialised requests.response object
# the value is a dict containing the endpoint, endpoint_args, endpoint_params and model
# so we can use this to call Client._deserialize(model, response) and check that the result is a valid pydantic model

def create_response_from_json(json_file) -> Response:
    with open(json_file, 'r') as f:
        serialised_response = json.load(f)
    response = Response()
    response.headers = serialised_response['headers']
    response.status_code = serialised_response['status_code']
    response.url = serialised_response['url']
    response._content = serialised_response['content'].encode("utf-8")
    return response

for resp in response_to_request_mapping:
    def test_deserialise_response(resp=resp):
        response = create_response_from_json(f"tests/tfl_responses/{resp}.json")
        expect_empty_response: bool = response_to_request_mapping[resp]["result_is_empty"]
        model = response_to_request_mapping[resp]["model"]
        client = Client()

        result = client._deserialize(model, response)
        # assert that result is not empty only if we expect it not to be
        assert (not expect_empty_response and result) or (expect_empty_response and not result)

    globals()[f"test_deserialise_response_{resp}"] = test_deserialise_response
