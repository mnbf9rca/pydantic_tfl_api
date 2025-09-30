#!/usr/bin/env python3
"""Entry point script for building Pydantic models using BuildCoordinator.

This script provides a CLI interface to the new modular build system.
"""

import argparse
import logging
import sys
from pathlib import Path

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from build_system.build_coordinator import BuildCoordinator  # type: ignore[import-not-found]

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def main(spec_path: str, output_path: str) -> None:
    """
    Main function to build Pydantic models from OpenAPI specifications.

    Args:
        spec_path: Path to the directory containing OpenAPI specification files
        output_path: Path to the directory where generated models will be saved

    Raises:
        FileNotFoundError: If spec_path doesn't exist
        ValueError: If specs are invalid or malformed
        Exception: For any other errors during model generation
    """
    try:
        coordinator = BuildCoordinator()
        coordinator.build(spec_path=spec_path, output_path=output_path)

        # Log final statistics
        stats = coordinator.get_build_stats()
        logging.info(f"Build completed successfully. Statistics: {stats}")

    except FileNotFoundError as e:
        logging.error(f"File not found error: {e}")
        sys.exit(1)
    except ValueError as e:
        logging.error(f"Value error during model generation: {e}")
        sys.exit(1)
    except PermissionError as e:
        logging.error(f"Permission error accessing files: {e}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Unexpected error during model generation: {e}", exc_info=True)
        sys.exit(1)

    logging.info("Processing complete.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Build Pydantic models from OpenAPI specifications using the modular build system."
    )
    parser.add_argument("specpath", help="Path to the directory containing OpenAPI specification files")
    parser.add_argument("output", help="Path to the output directory for generated code")

    args = parser.parse_args()

    main(args.specpath, args.output)
