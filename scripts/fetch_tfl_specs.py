#!/usr/bin/env python3
"""
Script to fetch TfL API specifications from the API portal and reconstruct OpenAPI 3.0 specs.
"""

import json
from pathlib import Path
from typing import Any

import requests


class TfLAPIFetcher:
    """Fetches TfL API specifications from the public API portal endpoints."""

    BASE_URL = "https://api-portal.tfl.gov.uk"
    API_VERSION = "2022-04-01-preview"

    def __init__(self) -> None:
        self.session = requests.Session()

    def get_all_apis(self) -> list[dict[str, Any]]:
        """Get list of all available APIs."""
        url = f"{self.BASE_URL}/developer/apis"
        params = {"api-version": self.API_VERSION}

        response = self.session.get(url, params=params)
        response.raise_for_status()

        data = response.json()
        return data.get("value", [])

    def get_api_details(self, api_id: str) -> dict[str, Any]:
        """Get detailed information about a specific API."""
        url = f"{self.BASE_URL}/developer/apis/{api_id}"
        params = {"expandApiVersionSet": "true", "api-version": self.API_VERSION}

        response = self.session.get(url, params=params)
        response.raise_for_status()

        return response.json()

    def get_api_operations(self, api_id: str) -> list[dict[str, Any]]:
        """Get all operations for a specific API."""
        url = f"{self.BASE_URL}/developer/apis/{api_id}/operations"
        params = {"$top": "50", "api-version": self.API_VERSION}

        response = self.session.get(url, params=params)
        response.raise_for_status()

        data = response.json()
        return data.get("value", [])

    def get_operation_details(self, api_id: str, operation_id: str) -> dict[str, Any]:
        """Get detailed information about a specific operation."""
        url = f"{self.BASE_URL}/developer/apis/{api_id}/operations/{operation_id}"
        params = {"api-version": self.API_VERSION}

        response = self.session.get(url, params=params)
        response.raise_for_status()

        return response.json()

    def get_schema(self, api_id: str, schema_id: str) -> dict[str, Any]:
        """Get schema definition."""
        url = f"{self.BASE_URL}/developer/apis/{api_id}/schemas/{schema_id}"
        params = {"api-version": self.API_VERSION}

        response = self.session.get(url, params=params)
        response.raise_for_status()

        return response.json()

    def build_openapi_spec(self, api_id: str) -> dict[str, Any]:
        """Build a complete OpenAPI 3.0 specification for an API."""
        print(f"Building OpenAPI spec for {api_id}...")

        # Get API details
        api_details = self.get_api_details(api_id)

        # Get all operations
        operations = self.get_api_operations(api_id)

        # Initialize OpenAPI spec structure
        openapi_spec: dict[str, Any] = {
            "openapi": "3.0.1",
            "info": {
                "title": api_details.get("name", api_id),
                "description": api_details.get("description", f"APIs relating to {api_id} and similar services"),
                "version": "1.0",
            },
            "servers": [{"url": f"https://api.tfl.gov.uk/{api_details.get('path', api_id)}"}],
            "paths": {},
            "components": {"schemas": {}},
        }

        # Process each operation
        schemas_to_fetch = set()

        for operation in operations:
            operation_id = operation["id"]
            print(f"  Processing operation: {operation_id}")

            # Get detailed operation info
            op_details = self.get_operation_details(api_id, operation_id)

            # Extract path and add to spec
            url_template = operation["urlTemplate"]
            if url_template not in openapi_spec["paths"]:
                openapi_spec["paths"][url_template] = {}

            # Build operation definition
            method = operation["method"].lower()
            operation_def = {
                "summary": operation["name"],
                "description": operation.get("description", ""),
                "operationId": operation_id,
                "responses": {},
            }

            # Process responses
            if "responses" in op_details and op_details["responses"]:
                for response in op_details["responses"]:
                    status_code = str(response.get("statusCode", 200))
                    response_def = {"description": response.get("description", "OK"), "content": {}}

                    # Process representations (different content types)
                    if "representations" in response:
                        for repr_data in response["representations"]:
                            content_type = repr_data.get("contentType", "application/json")
                            schema_id = repr_data.get("schemaId")

                            if schema_id:
                                schemas_to_fetch.add((api_id, schema_id))
                                response_def["content"][content_type] = {
                                    "schema": {"$ref": f"#/components/schemas/{schema_id}"}
                                }

                    operation_def["responses"][status_code] = response_def

            openapi_spec["paths"][url_template][method] = operation_def

        # Fetch all referenced schemas
        print(f"  Fetching {len(schemas_to_fetch)} schemas...")
        for api_id_for_schema, schema_id in schemas_to_fetch:
            try:
                schema_data = self.get_schema(api_id_for_schema, schema_id)
                if "document" in schema_data and "components" in schema_data["document"]:
                    # Merge schema components
                    schema_components = schema_data["document"]["components"]
                    if "schemas" in schema_components:
                        openapi_spec["components"]["schemas"].update(schema_components["schemas"])

            except requests.RequestException as e:
                print(f"    Warning: Could not fetch schema {schema_id}: {e}")

        return openapi_spec

    def save_all_specs(self, output_dir: str = "specs") -> None:
        """Download and save all API specifications."""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        apis = self.get_all_apis()
        print(f"Found {len(apis)} APIs")

        for api in apis:
            api_id = api["id"]
            api_name = api["name"]

            print(f"\nProcessing API: {api_name} (ID: {api_id})")

            try:
                spec = self.build_openapi_spec(api_id)

                # Save to file
                filename = f"{api_id}.json"
                filepath = output_path / filename

                with open(filepath, "w", encoding="utf-8") as f:
                    json.dump(spec, f, indent=2, ensure_ascii=False)

                print(f"  Saved: {filepath}")

            except Exception as e:
                print(f"  Error processing {api_name}: {e}")


def main() -> None:
    """Main function to demonstrate the API fetching."""
    fetcher = TfLAPIFetcher()

    # First, let's just test with the Line API
    print("Testing with Line API...")
    try:
        line_spec = fetcher.build_openapi_spec("Line")
        print(
            f"Generated spec with {len(line_spec['paths'])} paths and {len(line_spec['components']['schemas'])} schemas"
        )

        # Save it
        with open("Line_test.json", "w") as f:
            json.dump(line_spec, f, indent=2)
        print("Saved Line API spec to Line_test.json")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
