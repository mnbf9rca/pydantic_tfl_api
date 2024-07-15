# this suite tests that the pydantic models can deserialise the JSON responses from the TFL API
# it uses snapshot responses from the API on a day that there was some disruption etc.

from config_for_tests import response_to_request_mapping
from requests.models import Response

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
        serialised_response = f.read()
    response = Response()
    response.__setstate__(serialised_response)
    return response

for resp in response_to_request_mapping:
    # def test_deserialise_response(resp=resp):
    response = create_response_from_json(f"tests/tfl_responses/{resp}.json")
    endpoint = response_to_request_mapping[resp]["endpoint"]
    endpoint_args = response_to_request_mapping[resp]["endpoint_args"]
    endpoint_params = response_to_request_mapping[resp]["endpoint_params"]
    model = response_to_request_mapping[resp]["model"]
    client = Client()
    result = client._deserialize(model, response)
    assert result
    assert isinstance(result, client.models[model])
    # globals()[f"test_deserialise_response_{resp}"] = test_deserialise_response