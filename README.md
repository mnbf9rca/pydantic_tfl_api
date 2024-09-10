# pydantic tfl api

I originally used [TfL-python-api](https://github.com/dhilmathy/TfL-python-api) by @dhilmathy but that verision depends on the [msrest](https://github.com/Azure/msrest-for-python) package, which has been deprecated for 2+ years. I have created this package to replace it, using pydantic and requests.

This API returns data from the TfL API in a more pythonic way, using pydantic models. It's a thin wrapper around the TfL API, so you can use the TfL API documentation to see what data is available.

## Installation

```bash
pip install pydantic-tfl-api
```

or

```bash
poetry add pydantic-tfl-api
```

## Usage

Uses Pydantic so you can use the `model_dump_json()` method to fully expand all the objects in the result. See [Pydantic documentation](https://docs.pydantic.dev/latest/) for more help.

You can obtain an API key from [your profile page on the API portal](https://api-portal.tfl.gov.uk/profile) although you only need this if doing more than a dozen or so requests per minute.

```python
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
```
## Class structure



### Models

Pydantic models are used to represent the data returned by the TfL API, and are in the `models` module. There are circular references in the TfL API, so these are handled by using `ForwardRef` in the models. Overall, there are 117 Pydantic models in the package. Models are automatically generated from the TfL API OpenAPI documentation, so if the TfL API changes, the models will be updated to reflect this. Fields are 'santizied' to remove any reserved words in Python (`class` or `from` for example), but otherwise are identical to the TfL API. In some cases, the TfL response has no definition, so the model is a `Dict[str, Any]`.

Some of the TfL responses are arrays, and these are wrapped in a `RootModel` object, which contains the array in the `root` attribute - for example, a `LineArray` model contains an array of `Line` objects in the `root` attribute. See the [Pydantic documentation for more information on how to use RootModels](https://docs.pydantic.dev/latest/concepts/models/#rootmodel-and-custom-root-types).


Successful responses are wrapped in a `ResponseModel` object, which contains the cache expiry time (`content_expires` and `shared_expires`, which are the calculated expiry based on the HTTP response timestamp and the `maxage`/`s-maxage` header respectively) for use to calculate the time to live of the object, and to determine if the object is still valid - for example if implementing caching - and the response object (in the `content` attribute).
Failures return an `ApiError` object, which contains the HTTP status code and the error message.

### Clients

 There are dedicated clients for each of the TfL APIs. These all inherit from `core.Client`. The method names are the same as the path IDs in the TfL API documentation, unless they are reserved words in Python, in which case they are suffixed with `Query_` (there are currently none in the package).

Clients are automatically generated from the TfL API OpenAPI documentation, so if the TfL API changes, the clients will be updated to reflect this. Clients are available for all the TfL API endpoints, and are named after the endpoint, with the `Client` suffix. Methods are named after the path ID in the TfL API documentation, with the `Query_` prefix if the path ID is a reserved word in Python (there are none in the package as far as i know), and they take the same parameters as the TfL API documentation. Here are the current clients from the `endpoints` module:

```bash
endpoints
├── AccidentStatsClient.py
├── AirQualityClient.py
├── BikePointClient.py
├── CrowdingClient.py
├── JourneyClient.py
├── LiftDisruptionsClient.py
├── LineClient.py
├── ModeClient.py
├── OccupancyClient.py
├── PlaceClient.py
├── RoadClient.py
├── SearchClient.py
├── StopPointClient.py
├── VehicleClient.py
```

Here's a Mermaid visualisation of the Pydantic models (or [view online](https://mermaid-js.github.io/mermaid-live-editor/edit#pako:eNqVWNtu2zgQ_ZVCz0mwce1c_LBA1m5Sd9O1EQUpsMjLWJrYbGRSS1HOaoP8-47uvMlJCxStzjkzJIfDI8qvQSRiDKZBlECWzRlsJOwe-Sf6cxVFLEau5qiAJVdSQvHp-Ph3C_dpK9kMshwSVQwKHnDLogRbXrE9hij3LML7IsVMH9Di6pBqxkMkRbM9JHNMQapcopbNYvz6SrqSGDPKL_g92zG-qaV_sGdcCcbVMoryFHhU9MldTp_rEDsDuQL53KF1KjBjzUezurMtyA3OBOcYKSE9ExtSGDkPauYsk3mqMK5W0Gc2cT2fj2kwKqmTgTA9-gY5ShbdYZYKnuF3atOm2RaKEQWyIC5PVJXjm8glx-JdwSoBWp6cFdR5X5nEuYieaWdDBeX4c1DwboqHqjrDsluChtkQQUbbmWSKVtcM1iTWB7mGtjN18hY3BliqKsKRG8wM9gjNBhjEPaR6yX1akujy-vxmdpSf-cWaG0F6lWnZ3kZp8UXpLOyJoaVf8EzJPHIDlutMQec9LboCtbWQaubxDyGfLaLv6Ba6E7nCpTY7bXR7NqHC1BGVYDePK6UkW1PGZhD2pPrVa95oEnodfUzZmnosxx6vbUKKl7hzug725elSaN674E_Cp6CdzjOL-A4q2mJcla2ntGTmRB2Ht8BemGJEvRD5A1zy8DraWh5YZr26wTpp9AMkLGaqWNHRF7FtiH0Xhaj1rCUIlUgdp70VPCZHZfJaSIwgM0i30KWX9tUtnwy99bxc_6T5uEjrzCajH6yykb0HtCO-pV8S3IPduwOw52DQCY20tVSPGjMDhRshC0vRwkZy-6w3cF_r_jqgpeswW3PgBtFk9nJ3AuKZoNtILKR2znVYT-LiJeK1CpPwieseXt-goFtgui0GNSa02KUQ0Y0A4YMBvfG8Kw3L1s2Tw_KVFH2LejShkoheup_6R9be-6Gt0wBb8AOT5E8uXjid_tw4LB8SHSpHr7Aq0L2JvKev8ZjyHtKeYd17SrzyDEddoZ1fulbller206iz9-WlzdkO7A7oGpx3hMhrr39BqoB_4UoWIf6TI4_QjfKIfDbchGgCZx2uZCljlIYxu5puHHOKjds6CczbZZWBzAWv4p95pnbUBpmuM3bf2fh6DAeu32ch7mkExfTvNIMxvNXHdCvTExhF7R5_zcVtokuj76tn0KH2OiBwdse_9Z0sMys-sNz6MzWmmwINBAmd7RRlWWqfzj7cJlsemxsp8nSILF_2gwLtbdqfQk3dg06a0nA17w1xU3afWdZhgt6GdV_VuNXCnrbW431MiSlYJ2hsAPkq7NZsk2s3Db_S2VK_rEO7q5uW3zPk0rm1D_PaFLwb3z97bvLtU_N9kWXINyivE_Hi4e8lMH5LbxX7wuLGdQs2l685konVLWG8xHyC-stwwcnF9tB89bdRlaJ6Vxrf_AatX7DrubsBtaaxvupqfy3rU-wK7l-otsU1hX-lv7OEPmDLaZs-6cthraT5DtSXVUf7sKFt-MBkfB8aDaP_6GZAjvMPO1DlC--4VK9pXCQ4CnYod8DiYBq8lqLHQG2RJh5M6b8xPkGeqMfgkb-RFHIlwoJHwZQ-j_EoyNOYTL35fbIFU-DB9DX4N5gen12cn5xdjiaTyelkcjEej46CIpiejn87GX-eXJ5PTseXn8eT0fnbUfCfEJRhdDKaXJxPzieXp6PxOcWcHQVkYJttMH2CJKuz_11J68Hosq6E_N78Wlr-8_Y_OZA7FA)):

[![](https://mermaid.ink/img/pako:eNqVWNtu2zgQ_ZVCz0mwce1c_LBA1m5Sd9O1EQUpsMjLWJrYbGRSS1HOaoP8-47uvMlJCxStzjkzJIfDI8qvQSRiDKZBlECWzRlsJOwe-Sf6cxVFLEau5qiAJVdSQvHp-Ph3C_dpK9kMshwSVQwKHnDLogRbXrE9hij3LML7IsVMH9Di6pBqxkMkRbM9JHNMQapcopbNYvz6SrqSGDPKL_g92zG-qaV_sGdcCcbVMoryFHhU9MldTp_rEDsDuQL53KF1KjBjzUezurMtyA3OBOcYKSE9ExtSGDkPauYsk3mqMK5W0Gc2cT2fj2kwKqmTgTA9-gY5ShbdYZYKnuF3atOm2RaKEQWyIC5PVJXjm8glx-JdwSoBWp6cFdR5X5nEuYieaWdDBeX4c1DwboqHqjrDsluChtkQQUbbmWSKVtcM1iTWB7mGtjN18hY3BliqKsKRG8wM9gjNBhjEPaR6yX1akujy-vxmdpSf-cWaG0F6lWnZ3kZp8UXpLOyJoaVf8EzJPHIDlutMQec9LboCtbWQaubxDyGfLaLv6Ba6E7nCpTY7bXR7NqHC1BGVYDePK6UkW1PGZhD2pPrVa95oEnodfUzZmnosxx6vbUKKl7hzug725elSaN674E_Cp6CdzjOL-A4q2mJcla2ntGTmRB2Ht8BemGJEvRD5A1zy8DraWh5YZr26wTpp9AMkLGaqWNHRF7FtiH0Xhaj1rCUIlUgdp70VPCZHZfJaSIwgM0i30KWX9tUtnwy99bxc_6T5uEjrzCajH6yykb0HtCO-pV8S3IPduwOw52DQCY20tVSPGjMDhRshC0vRwkZy-6w3cF_r_jqgpeswW3PgBtFk9nJ3AuKZoNtILKR2znVYT-LiJeK1CpPwieseXt-goFtgui0GNSa02KUQ0Y0A4YMBvfG8Kw3L1s2Tw_KVFH2LejShkoheup_6R9be-6Gt0wBb8AOT5E8uXjid_tw4LB8SHSpHr7Aq0L2JvKev8ZjyHtKeYd17SrzyDEddoZ1fulbller206iz9-WlzdkO7A7oGpx3hMhrr39BqoB_4UoWIf6TI4_QjfKIfDbchGgCZx2uZCljlIYxu5puHHOKjds6CczbZZWBzAWv4p95pnbUBpmuM3bf2fh6DAeu32ch7mkExfTvNIMxvNXHdCvTExhF7R5_zcVtokuj76tn0KH2OiBwdse_9Z0sMys-sNz6MzWmmwINBAmd7RRlWWqfzj7cJlsemxsp8nSILF_2gwLtbdqfQk3dg06a0nA17w1xU3afWdZhgt6GdV_VuNXCnrbW431MiSlYJ2hsAPkq7NZsk2s3Db_S2VK_rEO7q5uW3zPk0rm1D_PaFLwb3z97bvLtU_N9kWXINyivE_Hi4e8lMH5LbxX7wuLGdQs2l685konVLWG8xHyC-stwwcnF9tB89bdRlaJ6Vxrf_AatX7DrubsBtaaxvupqfy3rU-wK7l-otsU1hX-lv7OEPmDLaZs-6cthraT5DtSXVUf7sKFt-MBkfB8aDaP_6GZAjvMPO1DlC--4VK9pXCQ4CnYod8DiYBq8lqLHQG2RJh5M6b8xPkGeqMfgkb-RFHIlwoJHwZQ-j_EoyNOYTL35fbIFU-DB9DX4N5gen12cn5xdjiaTyelkcjEej46CIpiejn87GX-eXJ5PTseXn8eT0fnbUfCfEJRhdDKaXJxPzieXp6PxOcWcHQVkYJttMH2CJKuz_11J68Hosq6E_N78Wlr-8_Y_OZA7FA?type=png)](https://mermaid-js.github.io/mermaid-live-editor/edit#pako:eNqVWNtu2zgQ_ZVCz0mwce1c_LBA1m5Sd9O1EQUpsMjLWJrYbGRSS1HOaoP8-47uvMlJCxStzjkzJIfDI8qvQSRiDKZBlECWzRlsJOwe-Sf6cxVFLEau5qiAJVdSQvHp-Ph3C_dpK9kMshwSVQwKHnDLogRbXrE9hij3LML7IsVMH9Di6pBqxkMkRbM9JHNMQapcopbNYvz6SrqSGDPKL_g92zG-qaV_sGdcCcbVMoryFHhU9MldTp_rEDsDuQL53KF1KjBjzUezurMtyA3OBOcYKSE9ExtSGDkPauYsk3mqMK5W0Gc2cT2fj2kwKqmTgTA9-gY5ShbdYZYKnuF3atOm2RaKEQWyIC5PVJXjm8glx-JdwSoBWp6cFdR5X5nEuYieaWdDBeX4c1DwboqHqjrDsluChtkQQUbbmWSKVtcM1iTWB7mGtjN18hY3BliqKsKRG8wM9gjNBhjEPaR6yX1akujy-vxmdpSf-cWaG0F6lWnZ3kZp8UXpLOyJoaVf8EzJPHIDlutMQec9LboCtbWQaubxDyGfLaLv6Ba6E7nCpTY7bXR7NqHC1BGVYDePK6UkW1PGZhD2pPrVa95oEnodfUzZmnosxx6vbUKKl7hzug725elSaN674E_Cp6CdzjOL-A4q2mJcla2ntGTmRB2Ht8BemGJEvRD5A1zy8DraWh5YZr26wTpp9AMkLGaqWNHRF7FtiH0Xhaj1rCUIlUgdp70VPCZHZfJaSIwgM0i30KWX9tUtnwy99bxc_6T5uEjrzCajH6yykb0HtCO-pV8S3IPduwOw52DQCY20tVSPGjMDhRshC0vRwkZy-6w3cF_r_jqgpeswW3PgBtFk9nJ3AuKZoNtILKR2znVYT-LiJeK1CpPwieseXt-goFtgui0GNSa02KUQ0Y0A4YMBvfG8Kw3L1s2Tw_KVFH2LejShkoheup_6R9be-6Gt0wBb8AOT5E8uXjid_tw4LB8SHSpHr7Aq0L2JvKev8ZjyHtKeYd17SrzyDEddoZ1fulbller206iz9-WlzdkO7A7oGpx3hMhrr39BqoB_4UoWIf6TI4_QjfKIfDbchGgCZx2uZCljlIYxu5puHHOKjds6CczbZZWBzAWv4p95pnbUBpmuM3bf2fh6DAeu32ch7mkExfTvNIMxvNXHdCvTExhF7R5_zcVtokuj76tn0KH2OiBwdse_9Z0sMys-sNz6MzWmmwINBAmd7RRlWWqfzj7cJlsemxsp8nSILF_2gwLtbdqfQk3dg06a0nA17w1xU3afWdZhgt6GdV_VuNXCnrbW431MiSlYJ2hsAPkq7NZsk2s3Db_S2VK_rEO7q5uW3zPk0rm1D_PaFLwb3z97bvLtU_N9kWXINyivE_Hi4e8lMH5LbxX7wuLGdQs2l685konVLWG8xHyC-stwwcnF9tB89bdRlaJ6Vxrf_AatX7DrubsBtaaxvupqfy3rU-wK7l-otsU1hX-lv7OEPmDLaZs-6cthraT5DtSXVUf7sKFt-MBkfB8aDaP_6GZAjvMPO1DlC--4VK9pXCQ4CnYod8DiYBq8lqLHQG2RJh5M6b8xPkGeqMfgkb-RFHIlwoJHwZQ-j_EoyNOYTL35fbIFU-DB9DX4N5gen12cn5xdjiaTyelkcjEej46CIpiejn87GX-eXJ5PTseXn8eT0fnbUfCfEJRhdDKaXJxPzieXp6PxOcWcHQVkYJttMH2CJKuz_11J68Hosq6E_N78Wlr-8_Y_OZA7FA)

# Development environment

The devcontainer is set up to use the `poetry` package manager. You can use the `poetry` commands to manage the environment. The `poetry.lock` file is checked in, so you can use `poetry install --with dev --no-interaction --sync --no-root` to install the dependencies (which the devcontainer does on the `postCreateCommand` command).