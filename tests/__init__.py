import os
import sys

# Detect target for testing
test_target = os.getenv('PYTHON_TEST_TARGET', 'src')  # Default to 'src'

if test_target == 'pydantic_tfl_api':
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../pydantic_tfl_api')))
else:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

# Optional logging for clarity during test runs
print(f"Running tests against {test_target} directory")