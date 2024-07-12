from pydantic_tfl_api.client import Client, ApiToken

app_id = 'APPLICATION ID'
app_key = 'APPLICATION KEY'

# token = ApiToken(app_id, app_key)
token = None # only need a token if > 1 request per second

client = Client(token)
print (client.get_line_meta_modes())
print (client.get_lines(mode="bus")[0].model_dump_json())
print (client.get_lines(line_id="victoria")[0].model_dump_json())
print (client.get_route_by_line_id_with_direction(line_id="northern", direction="all").model_dump_json())