import json
from typing import Any

from requests import Response

from pydantic_tfl_api.core import Client

# from pydantic_tfl_api.config import endpoints

app_key = "APPLICATION KEY"


token = None  # only need a token if > 1 request per second

client = Client(token)


def persist_json(response: Response, filename: str) -> None:
    if response.status_code != 200:
        print(f"Error: {response.status_code} for {filename}")
        return
    response_object = {
        "status_code": response.status_code,
        "headers": dict(response.headers),
        "url": response.url,
        "content": response.content.decode("utf-8"),
    }
    with open(filename, "w") as file:
        file.write(json.dumps(response_object))


# def get_and_save_response(endpoint, endpoint_args, endpoint_params, model, file_name):
#     ep = endpoints[endpoint].format(*endpoint_args)
#     response = client.client.send_request(ep, endpoint_params)
#     persist_json(response, f"tests/tfl_responses/{file_name}")


def create_request_name_from_args(request_args: dict[str, Any]) -> str:
    # format is {endpoint}_{endpoint_args}_{endpoint_params}_{model}
    # ensuring that we remove any commas from the endpoint_args
    # and mapping {} in endpoint_params to None

    endpoint_args = request_args.get("endpoint_args", "None")
    endpoint_args = "_".join(endpoint_args) if len(endpoint_args) > 0 else "None"
    endpoint_args = endpoint_args.replace(",", "_")

    # Simplify endpoint_params processing
    endpoint_params = request_args.get("endpoint_params", {})
    endpoint_params = "_".join(f"{k}_{v}" for k, v in endpoint_params.items()) if endpoint_params else "None"

    # Construct and return the request name
    return f"{request_args['endpoint']}_{endpoint_args}_{endpoint_params}_{request_args['model']}"


# for request_args in response_to_request_mapping:
#     request_name = create_request_name_from_args(request_args)
#     print(f"'{request_name}': {request_args}")

# for request in response_to_request_mapping:
#     # a request looks liek this: 'stopPointsByLineId_victoria_None_StopPoint': {'endpoint': 'stopPointsByLineId', 'endpoint_args': ['victoria'], 'endpoint_params': {}, 'model': 'StopPoint'}
#     get_and_save_response(
#         **response_to_request_mapping[request], file_name=f"{request}.json"
#     )
#     # get_and_save_response(**request_args, file_name=f"{request_name}.json")


# print (client.get_line_meta_modes())
# print (client.get_lines(mode="bus")[0].model_dump_json())
# print (client.get_lines(line_id=["victoria"])[0].model_dump_json())
# print (client.get_route_by_line_id_with_direction(line_id="northern", direction="all").model_dump_json())
