"""
Tests for package installation and import functionality.

This module tests that the built pydantic-tfl-api package:
1. Builds correctly using UV
2. Installs in an isolated environment
3. All modules and models can be imported
4. Package metadata is correct
5. Can successfully query the TfL API
"""

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

import pytest


class TestPackageInstallation:
    """Test suite for package building and installation."""

    @pytest.fixture(scope="class")
    def project_root(self) -> Any:
        """Get the project root directory."""
        return Path(__file__).parent.parent

    @pytest.fixture(scope="class")
    def built_package(self, project_root: Any) -> Any:
        """Build the package and return the wheel path."""
        # Clean any existing dist directory
        dist_dir = project_root / "dist"
        if dist_dir.exists():
            shutil.rmtree(dist_dir)

        # Build the package
        result = subprocess.run(["uv", "build"], cwd=project_root, capture_output=True, text=True, timeout=120)

        if result.returncode != 0:
            pytest.fail(f"Package build failed:\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}")

        # Find the built wheel
        wheels = list(dist_dir.glob("*.whl"))
        if not wheels:
            pytest.fail(f"No wheel file found in {dist_dir}")

        return wheels[0]

    @pytest.fixture(scope="class")
    def isolated_env(self, built_package: Any) -> Any:
        """Create an isolated environment with the package installed."""
        with tempfile.TemporaryDirectory(prefix="pydantic_tfl_test_") as temp_dir:
            env_dir = Path(temp_dir) / "test_env"

            # Create virtual environment
            result = subprocess.run(
                [sys.executable, "-m", "venv", str(env_dir)], capture_output=True, text=True, timeout=60
            )

            if result.returncode != 0:
                pytest.fail(f"Failed to create virtual environment:\n{result.stderr}")

            # Determine pip path based on OS
            if sys.platform == "win32":
                pip_path = env_dir / "Scripts" / "pip"
                python_path = env_dir / "Scripts" / "python"
            else:
                pip_path = env_dir / "bin" / "pip"
                python_path = env_dir / "bin" / "python"

            # Install the built package
            install_result = subprocess.run(
                [str(pip_path), "install", str(built_package)], capture_output=True, text=True, timeout=120
            )

            if install_result.returncode != 0:
                pytest.fail(f"Failed to install package:\n{install_result.stderr}")

            yield {"env_dir": env_dir, "python_path": python_path, "pip_path": pip_path}

    def test_package_builds_successfully(self, built_package: Any) -> None:
        """Test that the package builds without errors."""
        assert built_package.exists(), f"Built package not found: {built_package}"
        assert built_package.suffix == ".whl", f"Expected wheel file, got: {built_package}"

        # Check that the wheel file is not empty
        assert built_package.stat().st_size > 0, "Built wheel file is empty"

    def test_package_installs_successfully(self, isolated_env: Any) -> None:
        """Test that the package installs in an isolated environment."""
        python_path = isolated_env["python_path"]

        # Verify installation by listing installed packages
        result = subprocess.run([str(python_path), "-m", "pip", "list"], capture_output=True, text=True, timeout=30)

        assert result.returncode == 0, f"Failed to list packages: {result.stderr}"
        assert "pydantic-tfl-api" in result.stdout, "Package not found in installed packages"

    def test_main_package_imports(self, isolated_env: Any) -> None:
        """Test that the main package can be imported."""
        python_path = isolated_env["python_path"]

        # Test basic import
        result = subprocess.run(
            [str(python_path), "-c", "import pydantic_tfl_api; print('Import successful')"],
            capture_output=True,
            text=True,
            timeout=30,
        )

        assert result.returncode == 0, f"Failed to import main package: {result.stderr}"
        assert "Import successful" in result.stdout

    @pytest.mark.parametrize(
        "client",
        [
            # Sync clients
            "LineClient",
            "StopPointClient",
            "BikePointClient",
            "AirQualityClient",
            "JourneyClient",
            "PlaceClient",
            "RoadClient",
            "SearchClient",
            "VehicleClient",
            "ModeClient",
            "AccidentStatsClient",
            "CrowdingClient",
            "OccupancyClient",
            "LiftDisruptionsClient",
            # Async clients
            "AsyncLineClient",
            "AsyncStopPointClient",
            "AsyncBikePointClient",
            "AsyncAirQualityClient",
            "AsyncJourneyClient",
            "AsyncPlaceClient",
            "AsyncRoadClient",
            "AsyncSearchClient",
            "AsyncVehicleClient",
            "AsyncModeClient",
            "AsyncAccidentStatsClient",
            "AsyncCrowdingClient",
            "AsyncOccupancyClient",
            "AsyncLiftDisruptionsClient",
        ],
    )
    def test_client_imports(self, isolated_env: Any, client: Any) -> None:
        """Test that individual client classes can be imported."""
        python_path = isolated_env["python_path"]

        result = subprocess.run(
            [str(python_path), "-c", f"from pydantic_tfl_api import {client}; print('{client} imported')"],
            capture_output=True,
            text=True,
            timeout=30,
        )

        assert result.returncode == 0, f"Failed to import {client}: {result.stderr}"
        assert f"{client} imported" in result.stdout

    @pytest.mark.parametrize(
        "import_stmt",
        [
            "from pydantic_tfl_api.core import Client, ResponseModel, ApiError",
            "from pydantic_tfl_api.core import AsyncClient, AsyncRestClient",
            "from pydantic_tfl_api.core import HttpxClient, AsyncHttpxClient",
            "from pydantic_tfl_api.core import HTTPClientBase, AsyncHTTPClientBase",
            "from pydantic_tfl_api.core import get_default_http_client, get_default_async_http_client",
            "from pydantic_tfl_api.models import Line, LineArray, Mode, ModeArray",
        ],
    )
    def test_core_modules_import(self, isolated_env: Any, import_stmt: Any) -> None:
        """Test that individual core modules can be imported."""
        python_path = isolated_env["python_path"]

        result = subprocess.run(
            [str(python_path), "-c", f"{import_stmt}; print('Core import successful')"],
            capture_output=True,
            text=True,
            timeout=30,
        )

        assert result.returncode == 0, f"Failed to import core modules: {result.stderr}"
        assert "Core import successful" in result.stdout

    def test_package_version_consistency(self, isolated_env: Any) -> None:
        """Test that package version matches pyproject.toml."""
        python_path = isolated_env["python_path"]

        # Get version from installed package
        result = subprocess.run(
            [str(python_path), "-c", "import pydantic_tfl_api; print(pydantic_tfl_api.__version__)"],
            capture_output=True,
            text=True,
            timeout=30,
        )

        assert result.returncode == 0, f"Failed to get package version: {result.stderr}"

        installed_version = result.stdout.strip()

        # Read version from pyproject.toml
        project_root = Path(__file__).parent.parent
        content = (project_root / "pyproject.toml").read_text()

        # Extract version from pyproject.toml
        import re

        version_match = re.search(r'version = "([^"]+)"', content)
        assert version_match, "Could not find version in pyproject.toml"

        expected_version = version_match.group(1)

        assert (
            installed_version == expected_version
        ), f"Version mismatch: installed={installed_version}, expected={expected_version}"

    def test_package_can_query_tfl_api(self, isolated_env: Any) -> None:
        """Test that the installed package can successfully query the TfL API."""
        python_path = isolated_env["python_path"]

        # Test a simple API call that doesn't require authentication
        test_script = '''
import time
from pydantic_tfl_api import LineClient
from pydantic_tfl_api.core import ResponseModel, ApiError
from typing import Any


def validate_api_result(result: Any) -> bool:
    """Helper to validate API result without conditionals."""
    # Check for ApiError first
    if isinstance(result, ApiError):
        print(f"API Error: {result.http_status_code} - {result.http_status}")
        return False

    # Check for ResponseModel
    if not isinstance(result, ResponseModel):
        print(f"Unexpected result type: {type(result)}")
        return False

    return True

def validate_response_content(result: Any) -> bool:
    """Helper to validate response content structure."""
    if not hasattr(result.content, 'root'):
        print("Warning: No root attribute found")
        return True  # Still considered success

    if not result.content.root:
        print("Warning: Empty root content")
        return True  # Still considered success

    print(f"Number of modes: {len(result.content.root)}")
    print(f"First mode: {result.content.root[0].modeName}")
    return True

client = LineClient()
time.sleep(1)  # Rate limiting
result = client.MetaModes()

# Validate result using helper functions
if not validate_api_result(result):
    exit(1)

print("TfL API query successful")
print(f"Response type: {type(result.content)}")

if not validate_response_content(result):
    exit(1)
'''

        result = subprocess.run([str(python_path), "-c", test_script], capture_output=True, text=True, timeout=60)

        print(f"API test output: {result.stdout}")
        if result.stderr:  # sourcery skip: no-conditionals-in-tests
            print(f"API test errors: {result.stderr}")

        assert result.returncode == 0, f"TfL API query failed: {result.stderr}"
        assert "TfL API query successful" in result.stdout, "API query did not complete successfully"

    @pytest.mark.parametrize("dependency", ["pydantic", "httpx"])
    def test_package_dependencies_correct(self, isolated_env: Any, dependency: Any) -> None:
        """Test that individual package dependencies are installed correctly."""
        python_path = isolated_env["python_path"]

        result = subprocess.run(
            [str(python_path), "-c", f"import {dependency}; print('{dependency} available')"],
            capture_output=True,
            text=True,
            timeout=30,
        )

        assert result.returncode == 0, f"Required dependency {dependency} not available: {result.stderr}"
        assert f"{dependency} available" in result.stdout
