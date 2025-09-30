from pydantic_tfl_api import LineClient
from pydantic_tfl_api.core import ApiError

token = None  # only need a token if > 1 request per second

client = LineClient(token)

# Example 1: Basic usage with error handling
response_object = client.MetaModes()
if isinstance(response_object, ApiError):
    print(f"Error getting modes: {response_object.message}")
else:
    # the response object is a pydantic model
    # the `content` attribute is the API response, parsed into a pydantic model
    mode_array = response_object.content
    # if it's an array, it's wrapped in a `RootModel`, which means it has a root attribute containing the array
    array_content = mode_array.root
    print(array_content[0].modeName)

# Example 2: Chained operations with error handling
meta_modes_result = client.MetaModes()
if isinstance(meta_modes_result, ApiError):
    print(f"Error getting meta modes: {meta_modes_result.message}")
else:
    print(meta_modes_result.content.root[0].model_dump_json())

bus_modes_result = client.GetByModeByPathModes(modes="bus")
if isinstance(bus_modes_result, ApiError):
    print(f"Error getting bus modes: {bus_modes_result.message}")
else:
    print(bus_modes_result.content.root[0].model_dump_json())

# Example 3: Using the models directly with error handling
tube_status_result = client.StatusByModeByPathModesQueryDetailQuerySeverityLevel(modes="tube")
if isinstance(tube_status_result, ApiError):
    print(f"Error getting tube status: {tube_status_result.message}")
else:
    line_items = tube_status_result.content.root
    print([f"The {line_item.name} line is {line_item.modeName}" for line_item in line_items])

# Example 4: Complex data with error handling
route_sequence_result = client.RouteSequenceByPathIdPathDirectionQueryServiceTypesQueryExcludeCrowding(
    id="northern", direction="all"
)
if isinstance(route_sequence_result, ApiError):
    print(f"Error getting route sequence: {route_sequence_result.message}")
else:
    # some return enormous amounts of data with very complex models
    print(route_sequence_result.model_dump_json())
