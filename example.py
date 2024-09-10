from pydantic_tfl_api import LineClient

token = None # only need a token if > 1 request per second

client = LineClient(token)
response_object = client.MetaModes()
# the response object is a pydantic model
# the `content`` attribute is the API response, parsed into a pydantic model
mode_array = response_object.content
# if it's an array, it's a wrapped in a `RootModel``, which means it has a root attribute containing the array
array_content = mode_array.root

print(array_content[0].modeName)

# obviously, you can chain these together
print (client.MetaModes().content.root[0].model_dump_json())
print (client.GetByModeByPathModes(modes="bus").content.root[0].model_dump_json())

# you can also use the models directly
print ([f'The {line_item.name} line is {line_item.modeName}' for line_item in client.StatusByModeByPathModesQueryDetailQuerySeverityLevel(modes="tube").content.root])

# some return enormous amounts of data with very complex models
print(client.RouteSequenceByPathIdPathDirectionQueryServiceTypesQueryExcludeCrowding(id="northern", direction="all").model_dump_json())