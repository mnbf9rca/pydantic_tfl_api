#!/bin/bash
set -e

# Determine version bump type based on production dependency changes in pyproject.toml
# Compares dependency versions between main and release branches
# Returns: major, minor, or patch

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to compare semantic versions
# Returns: major, minor, patch, or none
compare_versions() {
    local old_ver="$1"
    local new_ver="$2"
    local dep_name="$3"

    # Remove any leading 'v' and extract major.minor.patch
    old_ver=$(echo "$old_ver" | sed 's/^v//' | grep -oE '^[0-9]+\.[0-9]+\.[0-9]+' || echo "$old_ver")
    new_ver=$(echo "$new_ver" | sed 's/^v//' | grep -oE '^[0-9]+\.[0-9]+\.[0-9]+' || echo "$new_ver")

    if [ "$old_ver" = "$new_ver" ]; then
        echo "none"
        return
    fi

    # Split versions into components
    IFS='.' read -r old_major old_minor old_patch <<< "$old_ver"
    IFS='.' read -r new_major new_minor new_patch <<< "$new_ver"

    # Compare major versions
    if [ "$new_major" -gt "$old_major" ]; then
        echo -e "${GREEN}[INFO]${NC} $dep_name: Major version bump detected ($old_ver → $new_ver)" >&2
        echo "major"
        return
    fi

    # Compare minor versions
    if [ "$new_major" -eq "$old_major" ] && [ "$new_minor" -gt "$old_minor" ]; then
        echo -e "${GREEN}[INFO]${NC} $dep_name: Minor version bump detected ($old_ver → $new_ver)" >&2
        echo "minor"
        return
    fi

    # Compare patch versions
    if [ "$new_major" -eq "$old_major" ] && [ "$new_minor" -eq "$old_minor" ] && [ "$new_patch" -gt "$old_patch" ]; then
        echo -e "${GREEN}[INFO]${NC} $dep_name: Patch version bump detected ($old_ver → $new_ver)" >&2
        echo "patch"
        return
    fi

    # Version decreased or invalid
    echo -e "${YELLOW}[WARN]${NC} $dep_name: Version changed but not a standard bump ($old_ver → $new_ver)" >&2
    echo "none"
}

# Function to extract dependency version from pyproject.toml using Python TOML parser
# Args: dependency name, branch name (for fetching file)
extract_dependency_version() {
    local dep_name="$1"
    local branch="$2"

    # Use Python with tomllib (Python 3.11+ built-in) or tomli fallback
    version=$(git show "${branch}:pyproject.toml" | python3 -c "
import sys
import re

try:
    # Python 3.11+ has tomllib in stdlib
    import tomllib
except ImportError:
    try:
        # Fallback to tomli (available as dev dependency)
        import tomli as tomllib
    except ImportError:
        print('__PARSER_ERROR__: tomllib/tomli not available', file=sys.stderr)
        sys.exit(1)

dep_name = sys.argv[1]
content = sys.stdin.read()

try:
    data = tomli.loads(content)
except Exception as e:
    print(f'__PARSE_ERROR__: {e}', file=sys.stderr)
    sys.exit(1)

# Get dependencies list
deps = data.get('project', {}).get('dependencies', [])

# Find the dependency
for dep in deps:
    if isinstance(dep, str) and dep.strip().startswith(dep_name):
        # Extract version using regex: matches >=X.Y.Z or ==X.Y.Z etc
        match = re.search(r'([><=!]+)?\s*([0-9]+\.[0-9]+\.[0-9]+)', dep)
        if match:
            print(match.group(2))
            sys.exit(0)

# Dependency not found
print('__NOT_FOUND__')
" "$dep_name" 2>&1)

    echo "$version"
}

echo -e "${GREEN}[INFO]${NC} Analyzing dependency changes between release and main branches..."

# Production dependencies to check
DEPENDENCIES=("pydantic" "requests")

# Default bump type
bump_type="patch"

echo -e "${GREEN}[INFO]${NC} Checking production dependencies..."

# Check each dependency
for dep in "${DEPENDENCIES[@]}"; do
    old_version=$(extract_dependency_version "$dep" "origin/release")
    new_version=$(extract_dependency_version "$dep" "origin/main")

    # Handle parser errors
    if [[ "$old_version" == __PARSER_ERROR__* ]] || [[ "$new_version" == __PARSER_ERROR__* ]]; then
        echo -e "${RED}[ERROR]${NC} Failed to parse pyproject.toml. Ensure tomli is installed." >&2
        echo "patch"  # Safe default
        exit 0
    fi

    # Handle parse errors
    if [[ "$old_version" == __PARSE_ERROR__* ]] || [[ "$new_version" == __PARSE_ERROR__* ]]; then
        echo -e "${RED}[ERROR]${NC} Failed to parse pyproject.toml format" >&2
        echo "patch"  # Safe default
        exit 0
    fi

    echo -e "${GREEN}[INFO]${NC} $dep: $old_version (release) vs $new_version (main)"

    # Handle new dependencies (added in main)
    if [ "$old_version" = "__NOT_FOUND__" ] && [ "$new_version" != "__NOT_FOUND__" ]; then
        echo -e "${YELLOW}[WARN]${NC} $dep: New dependency added in main ($new_version)" >&2
        # New dependency suggests minor bump (new functionality)
        if [ "$bump_type" = "patch" ]; then
            bump_type="minor"
        fi
        continue
    fi

    # Handle removed dependencies (removed from main)
    if [ "$old_version" != "__NOT_FOUND__" ] && [ "$new_version" = "__NOT_FOUND__" ]; then
        echo -e "${YELLOW}[WARN]${NC} $dep: Dependency removed from main" >&2
        # Removed dependency suggests major bump (breaking change)
        bump_type="major"
        continue
    fi

    # Handle both not found (dependency doesn't exist in either branch)
    if [ "$old_version" = "__NOT_FOUND__" ] && [ "$new_version" = "__NOT_FOUND__" ]; then
        echo -e "${YELLOW}[WARN]${NC} $dep: Dependency not found in either branch" >&2
        continue
    fi

    # Compare versions if both exist
    if [ "$old_version" != "$new_version" ]; then
        dep_bump=$(compare_versions "$old_version" "$new_version" "$dep")

        # Priority: major > minor > patch
        if [ "$dep_bump" = "major" ]; then
            bump_type="major"
        elif [ "$dep_bump" = "minor" ] && [ "$bump_type" != "major" ]; then
            bump_type="minor"
        elif [ "$dep_bump" = "patch" ] && [ "$bump_type" = "patch" ]; then
            bump_type="patch"
        fi
    fi
done

echo -e "${GREEN}[INFO]${NC} Determined bump type: ${YELLOW}${bump_type}${NC}"

# Output for GitHub Actions
echo "$bump_type"