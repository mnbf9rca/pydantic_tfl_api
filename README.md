# pydantic-tfl-api

Fully typed Python client for Transport for London (TfL) Unified API, using **Pydantic** for response validation and **httpx** as the default HTTP client (with optional `requests` support).

> **Note**: This package is **auto-generated** from TfL's OpenAPI specification. All client methods and response models **exactly mirror** the official TfL Unified API structure. This means method names and parameters match the TfL API documentation directly. You can [search the API portal to find what you need](https://api-portal.tfl.gov.uk/api-details), and then use the same names here.

Originally created as a replacement for [TfL-python-api](https://github.com/dhilmathy/TfL-python-api) which depends on the deprecated [msrest](https://github.com/Azure/msrest-for-python) package.

## What's changed in V3?

- major change: changed default http library has changed from `requests` to `httpx`. The Clients and APIs are all exactly the same and you should not notice any difference. See below for instructions on how to use `requests` if you prefer that.
- Added async clients. So for each client (e.g. `LineClient`) there's now an async couterpart (`AsyncLineClient`). Other behavior of the clients is identical.
- Fixed some parsing errors with the ApiError response. You will now always get either `ResponseModel` or `ApiError` when making requests (previously you may have had `ResponseModel[ApiError]` which was not expected behaviour).
- Removed CHANGELOG as it wasnt being maintained. Please refer to git history for changes.

## Installation

```bash
# Default installation (httpx - supports both sync and async)
pip install pydantic-tfl-api

# Or with uv
uv add pydantic-tfl-api
```

To use `requests` instead of `httpx` (sync only):

```bash
pip install pydantic-tfl-api[requests]
```

## Available API Clients

The package provides 14 API clients, each corresponding to a TfL API endpoint category. Import directly from `pydantic_tfl_api`:

```python
from pydantic_tfl_api import LineClient, StopPointClient, JourneyClient
```

| Client | Description |
|--------|-------------|
| `LineClient` | Tube, Overground, DLR, Elizabeth line status and information |
| `StopPointClient` | Bus stops, tube stations, piers, and other stop points |
| `JourneyClient` | Journey planning between locations |
| `VehicleClient` | Vehicle arrival predictions |
| `BikePointClient` | Santander Cycles docking stations |
| `AirQualityClient` | London air quality data and forecasts |
| `AccidentStatsClient` | Road accident statistics |
| `CrowdingClient` | Station crowding data |
| `OccupancyClient` | Bike point and car park occupancy |
| `PlaceClient` | Points of interest and places |
| `RoadClient` | Road corridor status and disruptions |
| `SearchClient` | Search for stops, stations, postcodes |
| `ModeClient` | Transport mode information |
| `LiftDisruptionsClient` | Lift and escalator disruption data |

**Async clients**: For async operations, prefix with `Async` (e.g., `AsyncLineClient`, `AsyncStopPointClient`).

## How It Works

This package is automatically generated from TfL's OpenAPI specification, which means:

1. **Client methods match TfL API operation IDs** - Method names come directly from the OpenAPI spec (e.g., `MetaModes`, `GetByModeByPathModes`, `StatusByIdsByPathIdsQueryDetail`)
2. **Parameters match the API exactly** - Path parameters include `ByPath` in the name, query parameters include `Query`
3. **All responses are Pydantic models** - Full validation, type hints, and IDE autocomplete
4. **117 Pydantic models** - Covering all TfL API response types

## Usage

### Basic Example (Annotated)

```python
from pydantic_tfl_api import LineClient

# Initialize client with your TfL API key
# Get a free key at: https://api-portal.tfl.gov.uk/profile
# Note: You only need a key for >1 request per second
client = LineClient(api_token="your_api_token_here")

# Call a method - names match TfL API operation IDs
# 'GetByModeByPathModes' = Get lines by mode, where mode is a path parameter
response = client.GetByModeByPathModes(modes="tube")

# Response is wrapped in ResponseModel with cache info
# - response.content: The actual data (Pydantic model)
# - response.content_expires: Cache expiry time
# - response.shared_expires: Shared cache expiry time

# For array responses, data is in a RootModel with .root attribute
lines = response.content.root

# Each item is a fully-typed Pydantic model
for line in lines:
    print(f"{line.id}: {line.name}")  # e.g., "victoria: Victoria"

    # Nested data is also typed
    if line.lineStatuses:
        for status in line.lineStatuses:
            print(f"  Status: {status.statusSeverityDescription}")
```

### Understanding Method Names

Method names are generated from TfL's OpenAPI operation IDs. Here's the pattern:

```python
from pydantic_tfl_api import LineClient

client = LineClient(api_token="your_key")

# Simple methods - just the operation name
response = client.MetaModes()  # GET /Line/Meta/Modes

# Methods with path parameters - "ByPath{ParamName}"
response = client.GetByModeByPathModes(modes="tube")  # GET /Line/Mode/{modes}

# Methods with query parameters - "Query{ParamName}"
response = client.StatusByIdsByPathIdsQueryDetail(
    ids="victoria",           # Path parameter
    detail=True               # Query parameter
)  # GET /Line/{ids}/Status?detail=true

# Complex method example
response = client.StatusByModeByPathModesQueryDetailQuerySeverityLevel(
    modes="tube",             # Path parameter
    detail=True,              # Query parameter
    severityLevel="Minor"     # Query parameter
)
```

### Discovering Available Methods

```python
from pydantic_tfl_api import LineClient

client = LineClient()

# List all available methods
public_methods = [m for m in dir(client) if not m.startswith('_') and callable(getattr(client, m))]
print(public_methods)
# ['ArrivalsByPathIds', 'DisruptionByModeByPathModes', 'GetByModeByPathModes',
#  'GetByPathIds', 'MetaDisruptionCategories', 'MetaModes', 'MetaSeverity', ...]

# Get help on a specific method (shows signature and parameters)
help(client.StatusByIdsByPathIdsQueryDetail)
```

### Working with Response Models

All responses are Pydantic models with full type hints and validation:

```python
from pydantic_tfl_api import LineClient

client = LineClient(api_token="your_key")
response = client.StatusByIdsByPathIdsQueryDetail(ids="victoria", detail=True)

# Check for errors
from pydantic_tfl_api.core import ApiError
if isinstance(response, ApiError):
    print(f"Error {response.httpStatusCode}: {response.message}")
else:
    # Access the typed response data
    for line in response.content.root:
        print(f"Line: {line.name}")
        print(f"Mode: {line.modeName}")

        for status in line.lineStatuses:
            print(f"  Severity: {status.statusSeverity}")
            print(f"  Description: {status.statusSeverityDescription}")
            print(f"  Reason: {status.reason}")

    # Convert to JSON
    print(response.content.model_dump_json(indent=2))

    # Access cache information
    print(f"Expires: {response.content_expires}")
```

### Async Example

For concurrent requests, use async clients (requires httpx - the default):

```python
import asyncio
from pydantic_tfl_api import AsyncLineClient

async def get_multiple_lines():
    # Create async client
    client = AsyncLineClient(api_token="your_key")

    # Fetch multiple lines concurrently
    victoria, central, northern = await asyncio.gather(
        client.StatusByIdsByPathIdsQueryDetail(ids="victoria"),
        client.StatusByIdsByPathIdsQueryDetail(ids="central"),
        client.StatusByIdsByPathIdsQueryDetail(ids="northern")
    )

    return victoria, central, northern

# Run the async function
results = asyncio.run(get_multiple_lines())
for result in results:
    print(result.content.root[0].name)
```

## HTTP Client Selection

By default, the package uses **httpx** which supports both sync and async operations.

To use `requests` instead (sync only):

```python
from pydantic_tfl_api import LineClient
from pydantic_tfl_api.core import RequestsClient

# Create a requests-based HTTP client
http_client = RequestsClient()

# Pass it to any API client
client = LineClient(api_token="your_key", http_client=http_client)
response = client.MetaModes()
```

## Class Structure

### Models

The package includes 117 Pydantic models representing all TfL API response types. Models are in the `models` module:

```python
from pydantic_tfl_api import models

# Access any model directly
line = models.Line(id="victoria", name="Victoria", ...)
```

Key points about models:

- **Circular references** are handled using `ForwardRef`
- **Field names match the API** except for Python reserved words (e.g., `class` → `class_`)
- **Array responses** are wrapped in `RootModel` (access via `.root` attribute)
- **Unknown fields** use `Dict[str, Any]` when TfL provides no schema

See the [Mermaid class diagram](https://mermaid-js.github.io/mermaid-live-editor/edit#pako:eNqVWNtu2zgQ_ZVCz0mwce1c_LBA1m5Sd9O1EQUpsMjLWJrYbGRSS1HOaoP8-47uvMlJCxStzjkzJIfDI8qvQSRiDKZBlECWzRlsJOwe-Sf6cxVFLEau5qiAJVdSQvHp-Ph3C_dpK9kMshwSVQwKHnDLogRbXrE9hij3LML7IsVMH9Di6pBqxkMkRbM9JHNMQapcopbNYvz6SrqSGDPKL_g92zG-qaV_sGdcCcbVMoryFHhU9MldTp_rEDsDuQL53KF1KjBjzUezurMtyA3OBOcYKSE9ExtSGDkPauYsk3mqMK5W0Gc2cT2fj2kwKqmTgTA9-gY5ShbdYZYKnuF3atOm2RaKEQWyIC5PVJXjm8glx-JdwSoBWp6cFdR5X5nEuYieaWdDBeX4c1DwboqHqjrDsluChtkQQUbbmWSKVtcM1iTWB7mGtjN18hY3BliqKsKRG8wM9gjNBhjEPaR6yX1akujy-vxmdpSf-cWaG0F6lWnZ3kZp8UXpLOyJoaVf8EzJPHIDlutMQec9LboCtbWQaubxDyGfLaLv6Ba6E7nCpTY7bXR7NqHC1BGVYDePK6UkW1PGZhD2pPrVa95oEnodfUzZmnosxx6vbUKKl7hzug725elSaN674E_Cp6CdzjOL-A4q2mJcla2ntGTmRB2Ht8BemGJEvRD5A1zy8DraWh5YZr26wTpp9AMkLGaqWNHRF7FtiH0Xhaj1rCUIlUgdp70VPCZHZfJaSIwgM0i30KWX9tUtnwy99bxc_6T5uEjrzCajH6yykb0HtCO-pV8S3IPduwOw52DQCY20tVSPGjMDhRshC0vRwkZy-6w3cF_r_jqgpeswW3PgBtFk9nJ3AuKZoNtILKR2znVYT-LiJeK1CpPwieseXt-goFtgui0GNSa02KUQ0Y0A4YMBvfG8Kw3L1s2Tw_KVFH2LejShkoheup_6R9be-6Gt0wBb8AOT5E8uXjid_tw4LB8SHSpHr7Aq0L2JvKev8ZjyHtKeYd17SrzyDEddoZ1fulbpler206iz9-WlzdkO7A7oGpx3hMhrr39BqoB_4UoWIf6TI4_QjfKIfDbchGgCZx2uZCljlIYxu5puHHOKjds6CczbZZWBzAWv4p95pnbUBpmuM3bf2fh6DAeu32ch7mkExfTvNIMxvNXHdCvTExhF7R5_zcVtokuj76tn0KH2OiBwdse_9Z0sMys-sNz6MzWmmwINBAmd7RRlWWqfzj7cJlsemxsp8nSILF_2gwLtbdqfQk3dg06a0nA17w1xU3afWdZhgt6GdV_VuNXCnrbW431MiSlYJ2hsAPkq7NZsk2s3Db_S2VK_rEO7q5uW3zPk0rm1D_PaFLwb3z97bvLtU_N9kWXINyivE_Hi4e8lMH5LbxX7wuLGdQs2l685konVLWG8xHyC-stwwcnF9tB89bdRlaJ6Vxrf_AatX7DrubsBtaaxvupqfy3rU-wK7l-otsU1hX-lv7OEPmDLaZs-6cthraT5DtSXVUf7sKFt-MBkfB8aDaP_6GZAjvMPO1DlC--4VK9pXCQ4CnYod8DiYBq8lqLHQG2RJh5M6b8xPkGeqMfgkb-RFHIlwoJHwZQ-j_EoyNOYTL35fbIFU-DB9DX4N5gen12cn5xdjiaTyelkcjEej46CIpiejn87GX-eXJ5PTseXn8eT0fnbUfCfEJRhdDKaXJxPzieXp6PxOcWcHQVkYJttMH2CJKuz_11J68Hosq6E_N78Wlr-8_Y_OZA7FA) for a visualization of all models.

### Clients

Clients are in the `endpoints` module and inherit from `core.Client` (sync) or `core.AsyncClient` (async). All 14 API categories have both sync and async versions.

## Development Environment

The devcontainer uses the `uv` package manager. The `uv.lock` file is checked in, so dependencies are installed automatically.

Common development commands:

```bash
uv sync                          # Install dependencies
uv run pytest                    # Run tests
uv run black .                   # Format code
uv run flake8 .                  # Lint code
uv build                         # Build the package
```

To test the build:

```bash
./build.sh "/workspaces/pydantic_tfl_api/pydantic_tfl_api" "/workspaces/pydantic_tfl_api/TfL_OpenAPI_specs" True
```

## Contributing

Contributions are welcome! Please note that this is a code-generated package - modifications should be made to the generation scripts in `/scripts/build_system/`, not to the generated files in `/pydantic_tfl_api/endpoints/` or `/pydantic_tfl_api/models/`.

## License

MIT License
